from typing import Set, Union, cast

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from sqlalchemy.sql.expression import and_

from lineapy.data.graph import Graph
from lineapy.data.types import *
from lineapy.db.asset_manager.local import LocalDataAssetManager, DataAssetManager
from lineapy.db.base import LineaDBConfig, LineaDB
from lineapy.db.relational.schema.relational import *
from lineapy.execution.executor import Executor
from lineapy.utils import CaseNotHandledError, NullValueError

LineaIDAlias = Union[LineaID, LineaIDORM]


class RelationalLineaDB(LineaDB):
    """
    - Note that LineaDB coordinates with assset manager and relational db.
      - The asset manager deals with binaries (e.g., cached values) - the relational db deals with more structured data,
      such as the Nodes and edges.
    - Also, at some point we might have a "cache" such that the readers don't have to go to the database if it's already
    ready, but that's lower priority.
    """

    def __init__(self):
        self._data_asset_manager: Optional[DataAssetManager] = None

    @property
    def session(self) -> scoped_session:
        if self._session:
            return self._session
        raise NullValueError("db should have been initialized")

    @session.setter
    def session(self, value):
        self._session = value

    def init_db(self, config: LineaDBConfig):
        # TODO: we eventually need some configurations
        # create_engine params from
        # https://stackoverflow.com/questions/21766960/operationalerror-no-such-table-in-flask-with-sqlalchemy
        engine = create_engine(
            config.database_uri,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
            echo=True,
        )
        self.session = scoped_session(sessionmaker())
        self.session.configure(bind=engine)
        Base.metadata.create_all(engine)

        self._data_asset_manager = LocalDataAssetManager(self.session)

    @staticmethod
    def get_orm(node: Node) -> NodeORM:
        pydantic_to_orm = {
            NodeType.ArgumentNode: ArgumentNodeORM,
            NodeType.CallNode: CallNodeORM,
            NodeType.ImportNode: ImportNodeORM,
            NodeType.LiteralAssignNode: LiteralAssignNodeORM,
            NodeType.FunctionDefinitionNode: FunctionDefinitionNodeORM,
            NodeType.ConditionNode: ConditionNodeORM,
            NodeType.LoopNode: LoopNodeORM,
            NodeType.DataSourceNode: DataSourceNodeORM,
            NodeType.StateChangeNode: StateChangeNodeORM,
            NodeType.VariableAliasNode: VariableAliasNodeORM,
        }

        return pydantic_to_orm[node.node_type]  # type: ignore

    @staticmethod
    def get_pydantic(node: NodeORM) -> Node:
        orm_to_pydantic = {
            NodeType.ArgumentNode: ArgumentNode,
            NodeType.CallNode: CallNode,
            NodeType.ImportNode: ImportNode,
            NodeType.LiteralAssignNode: LiteralAssignNode,
            NodeType.FunctionDefinitionNode: FunctionDefinitionNode,
            NodeType.ConditionNode: ConditionNode,
            NodeType.LoopNode: LoopNode,
            NodeType.DataSourceNode: DataSourceNode,
            NodeType.StateChangeNode: StateChangeNode,
            NodeType.VariableAliasNode: VariableAliasNode,
        }

        return orm_to_pydantic[node.node_type]  # type: ignore

    @staticmethod
    def get_type(val: Any) -> LiteralType:
        def is_integer(val):
            try:
                int(val)
            except Exception as e:
                return False
            return True

        if isinstance(val, str):
            return LiteralType.String
        elif is_integer(val):
            return LiteralType.Integer
        elif isinstance(val, bool):
            return LiteralType.Boolean
        raise CaseNotHandledError("Literal is not string, int, or boolean")

    @staticmethod
    def cast_serialized(val: str, literal_type: LiteralType) -> Any:
        if literal_type is LiteralType.Integer:
            return int(val)
        elif literal_type is LiteralType.Boolean:
            return val == "True"
        return val

    @staticmethod
    def cast_dataset(val: Any) -> Optional[str]:
        if hasattr(val, "to_csv"):
            return val.to_csv(index=False)
        return None

    """
    Writers
    """

    @property
    def data_asset_manager(self) -> DataAssetManager:
        if self._data_asset_manager:
            return self._data_asset_manager
        raise NullValueError("data asset manager should have been initialized")

    @data_asset_manager.setter
    def data_asset_manager(self, value: DataAssetManager) -> None:
        self._data_asset_manager = value

    def write_context(self, context: SessionContext) -> None:
        args = context.dict()

        if context.libraries:
            for i in range(len(args["libraries"])):
                lib_args = context.libraries[i].dict()
                lib_args["session_id"] = context.id
                library_orm = LibraryORM(**lib_args)
                self.session.add(library_orm)

                args["libraries"][i] = library_orm
        else:
            args["libraries"] = []

        context_orm = SessionContextORM(**args)

        self.session.add(context_orm)
        self.session.commit()

    def write_nodes(self, nodes: List[Node]) -> None:
        for n in nodes:
            self.write_single_node(n)

    def write_node_values(self, nodes: List[Node], version: int) -> None:
        for n in nodes:
            self.write_single_node_value(n, version)

    def write_single_node(self, node: Node) -> None:
        args = node.dict()
        if node.node_type is NodeType.ArgumentNode:
            node = cast(ArgumentNode, node)
            if args["value_literal"] is not None:
                args["value_literal_type"] = RelationalLineaDB.get_type(
                    args["value_literal"]
                )

        elif node.node_type is NodeType.CallNode:
            node = cast(CallNodeORM, node)
            for arg in node.arguments:
                self.session.execute(
                    call_node_association_table.insert(),
                    params={"call_node_id": node.id, "argument_node_id": arg},
                )
            del args["arguments"]
            del args["value"]

        elif node.node_type in [
            NodeType.LoopNode,
            NodeType.ConditionNode,
            NodeType.FunctionDefinitionNode,
        ]:
            node = cast(SideEffectsNodeORM, node)

            if node.state_change_nodes is not None:
                for state_change_id in node.state_change_nodes:
                    self.session.execute(
                        side_effects_state_change_association_table.insert(),
                        params={
                            "side_effects_node_id": node.id,
                            "state_change_node_id": state_change_id,
                        },
                    )

            if node.import_nodes is not None:
                for import_id in node.import_nodes:
                    self.session.execute(
                        side_effects_import_association_table.insert(),
                        params={
                            "side_effects_node_id": node.id,
                            "import_node_id": import_id,
                        },
                    )

            if node.node_type is NodeType.ConditionNode:
                node = cast(ConditionNode, node)
                if node.dependent_variables_in_predicate is not None:

                    for dependent_id in node.dependent_variables_in_predicate:
                        self.session.execute(
                            condition_association_table.insert(),
                            params={
                                "condition_node_id": node.id,
                                "dependent_node_id": dependent_id,
                            },
                        )
                    del args["dependent_variables_in_predicate"]

            del args["state_change_nodes"]
            del args["import_nodes"]

        elif node.node_type is NodeType.ImportNode:
            node = cast(ImportNodeORM, node)
            args["library_id"] = node.library.id
            del args["library"]
            del args["module"]

        elif node.node_type is NodeType.StateChangeNode:
            del args["value"]

        elif node.node_type is NodeType.LiteralAssignNode:
            node = cast(LiteralAssignNodeORM, node)
            args["value_type"] = RelationalLineaDB.get_type(node.value)

        node_orm = RelationalLineaDB.get_orm(node)(**args)

        self.session.add(node_orm)
        self.session.commit()

        self.write_single_node_value(node, version=1)

    def write_single_node_value(self, node: Node, version: int) -> None:
        self.data_asset_manager.write_node_value(node, version)

    def add_node_id_to_artifact_table(
        self,
        node_id: LineaIDORM,
        context_id: LineaIDORM,
        name: str = "",
        date_created: str = "",
        value_type: str = "",
    ) -> None:
        """
        Given that whether something is an artifact is just a human annotation, we are going to _exclude_ the information from the Graph Node types and just have a table that tracks what Node IDs are deemed as artifacts.
        """
        # - check node type: should just be CallNode and FunctionDefinitionNode
        #
        # - then insert into a table that's literally just the NodeID and maybe a timestamp for when it was registered as artifact

        node = self.get_node_by_id(node_id)
        if node.node_type in [NodeType.CallNode, NodeType.FunctionDefinitionNode]:
            artifact = ArtifactORM(
                id=node_id,
                context=context_id,
                value_type=value_type,
                name=name,
                date_created=date_created,
            )
            self.session.add(artifact)
            self.session.commit()

    def remove_node_id_from_artifact_table(self, node_id: LineaIDORM) -> None:
        """
        The opposite of write_node_is_artifact
        - for now we can just delete it directly
        """
        self.session.query(ArtifactORM).filter(ArtifactORM.id == node_id).delete()
        self.session.commit()

    """
    Readers
    """

    def get_nodes_by_file_name(self, file_name: str):
        """
        First queries SessionContext for file_name
        Then find all the nodes by session_id
        Note:
        - This is currently used for testing purposes
        - TODO: finish enumerating over all the tables (just a subset for now)
        - FIXME: I wonder if there is a way to write this in a single query, I would refer for the database to optimize this instead of relying on the ORM.
        """
        session_context = (
            self.session.query(SessionContextORM)
            .filter(SessionContextORM.file_name == file_name)
            .one()
        )
        # enumerating over all the tables...
        call_nodes = (
            self.session.query(CallNodeORM)
            .filter(CallNodeORM.session_id == session_context.id)
            .all()
        )
        argument_nodes = (
            self.session.query(ArgumentNodeORM)
            .filter(ArgumentNodeORM.session_id == session_context.id)
            .all()
        )
        call_nodes.extend(argument_nodes)
        nodes = [self.map_orm_to_pydantic(node) for node in call_nodes]
        return nodes

    def get_context(self, linea_id: LineaIDORM) -> SessionContext:
        query_obj = (
            self.session.query(SessionContextORM)
            .filter(SessionContextORM.id == linea_id)
            .one()
        )
        obj = SessionContext.from_orm(query_obj)
        return obj

    def get_nodes_from_db(self) -> List[Node]:
        node_orms = self.session.query(NodeORM).all()
        nodes = []
        for orm in node_orms:
            nodes.append(self.get_node_by_id(orm.id))
        return nodes

    def get_node_by_id(self, linea_id: LineaIDAlias) -> Node:
        """
        Returns the node by looking up the database by ID
        SQLAlchemy is able to translate between the two types on demand
        """
        # linea_id_orm = LineaIDORM().process_bind_param(linea_id)
        node = self.session.query(NodeORM).filter(NodeORM.id == linea_id).one()
        return self.map_orm_to_pydantic(node)

    def map_orm_to_pydantic(self, node: NodeORM) -> Node:
        # cast string serialized values to their appropriate types
        if node.node_type is NodeType.LiteralAssignNode:
            node = cast(LiteralAssignNodeORM, node)
            node.value = RelationalLineaDB.cast_serialized(node.value, node.value_type)
        elif node.node_type is NodeType.ArgumentNode:
            node = cast(ArgumentNodeORM, node)
            if node.value_literal is not None:
                node.value_literal = RelationalLineaDB.cast_serialized(
                    node.value_literal, node.value_literal_type
                )
        elif node.node_type is NodeType.ImportNode:
            node = cast(ImportNodeORM, node)
            library_orm = (
                self.session.query(LibraryORM)
                .filter(LibraryORM.id == node.library_id)
                .one()
            )
            node.library = Library.from_orm(library_orm)
        elif node.node_type is NodeType.CallNode:
            node = cast(CallNodeORM, node)
            arguments = (
                self.session.query(call_node_association_table)
                .filter(call_node_association_table.c.call_node_id == node.id)
                .all()
            )
            node.arguments = [a.argument_node_id for a in arguments]

        # TODO: find a way to have this just check for SideEffectsNode type
        elif node.node_type in [
            NodeType.LoopNode,
            NodeType.ConditionNode,
            NodeType.FunctionDefinitionNode,
        ]:
            node = cast(SideEffectsNodeORM, node)
            state_change_nodes = (
                self.session.query(side_effects_state_change_association_table)
                .filter(
                    side_effects_state_change_association_table.c.side_effects_node_id
                    == node.id
                )
                .all()
            )

            if state_change_nodes is not None:
                node.state_change_nodes = [
                    a.state_change_node_id for a in state_change_nodes
                ]

            import_nodes = (
                self.session.query(side_effects_import_association_table)
                .filter(
                    side_effects_import_association_table.c.side_effects_node_id
                    == node.id
                )
                .all()
            )

            if import_nodes is not None:
                node.import_nodes = [a.import_node_id for a in import_nodes]

            if node.node_type is NodeType.ConditionNode:
                node = cast(ConditionNodeORM, node)
                dependent_variables_in_predicate = (
                    self.session.query(condition_association_table)
                    .filter(condition_association_table.c.condition_node_id == node.id)
                    .all()
                )

                if dependent_variables_in_predicate is not None:
                    node.dependent_variables_in_predicate = [
                        a.dependent_node_id for a in dependent_variables_in_predicate
                    ]

        return RelationalLineaDB.get_pydantic(node).from_orm(node)

    def get_node_value(
        self, node_id: LineaIDAlias, version: int
    ) -> Optional[NodeValue]:
        value_orm = (
            self.session.query(NodeValueORM)
            .filter(
                and_(NodeValueORM.node_id == node_id, NodeValueORM.version == version)
            )
            .first()
        )
        if value_orm is not None:
            return value_orm.value
        return None

    def get_artifact(self, artifact_id: LineaIDAlias) -> Optional[Artifact]:
        return Artifact.from_orm(
            self.session.query(ArtifactORM)
            .filter(ArtifactORM.id == artifact_id)
            .first()
        )

    @staticmethod
    def get_node_value_type(node_value):
        # check object type (for now this only supports DataFrames, PIL images, and values)
        # TODO: need more robust type checking
        if hasattr(node_value, "to_csv"):
            return DATASET_TYPE
        elif hasattr(node_value, "show"):
            return CHART_TYPE
        return VALUE_TYPE

    def jsonify_artifact(self, artifact: Artifact) -> Dict:
        json_artifact = artifact.dict()

        json_artifact["type"] = json_artifact["value_type"]
        del json_artifact["value_type"]

        json_artifact["date"] = json_artifact["date_created"]
        del json_artifact["date_created"]

        json_artifact["file"] = ""

        json_artifact["code"] = {}
        json_artifact["code"]["text"] = self.get_code_from_artifact_id(artifact.id)

        tokens_json = []

        for node in self.get_graph_from_artifact_id(artifact.id).nodes:
            if node.node_type is not NodeType.CallNode:
                continue

            start_col = node.col_offset + 1
            end_col = node.end_col_offset + 1
            if node.assigned_variable_name is not None:
                end_col = len(node.assigned_variable_name) + start_col

            token_json = {
                "id": node.id,
                "line": node.lineno,
                "start": start_col,
                "end": end_col,
            }

            intermediate_value = (
                self.session.query(NodeValueORM)
                .filter(NodeValueORM.node_id == node.id)
                .first()
                .value
            )

            if intermediate_value is None:
                continue

            intermediate_value_type = RelationalLineaDB.get_node_value_type(
                intermediate_value
            )
            if intermediate_value_type == DATASET_TYPE:
                intermediate_value = RelationalLineaDB.cast_dataset(intermediate_value)
            elif intermediate_value_type == VALUE_TYPE:
                intermediate_value = RelationalLineaDB.cast_serialized(
                    intermediate_value, RelationalLineaDB.get_type(intermediate_value)
                )
            elif intermediate_value_type == CHART_TYPE:
                continue

            intermediate = {
                "file": "",
                "id": node.id,
                "name": "",
                "type": intermediate_value_type,
                "date": "1372944000",
                "text": intermediate_value,
            }
            token_json["intermediate"] = intermediate
            tokens_json.append(token_json)

        json_artifact["code"]["tokens"] = tokens_json

        return json_artifact

    def get_graph_from_artifact_id(self, artifact_id: LineaIDAlias) -> Graph:
        """
        - This is program slicing over database data.
        - There are lots of complexities when it comes to mutation
          - Examples:
            - Third party libraries have functions that mutate some global or variable state.
          - Strategy for now
            - definitely take care of the simple cases, like `VariableAliasNode`
            - simple heuristics that may create false positives (include things not necessary)
            - but definitely NOT false negatives (then the program CANNOT be executed)
        """
        nodes = self.get_nodes_from_db()
        full_graph = Graph(nodes)
        artifact = full_graph.get_node(artifact_id)
        ancestors = full_graph.get_ancestors(artifact)
        ancestors.append(artifact_id)
        return Graph([full_graph.get_node(a) for a in ancestors])

    def filter_subsumed_nodes(self, nodes: List[Node]) -> List[Node]:
        """
        Filters out nodes that are contained by other nodes
        e.g. removes an ArgumentNode subsumed by a CallNode's code
        """
        current_node = nodes[0]
        nodes_filtered = [current_node]

        for node in nodes:
            if node.lineno > current_node.end_lineno or (
                node.lineno == current_node.end_lineno
                and node.col_offset >= current_node.end_col_offset
            ):
                current_node = node
                nodes_filtered.append(current_node)

        return nodes_filtered

    def get_code_from_artifact_id(self, artifact_id: LineaID) -> str:
        graph = self.get_graph_from_artifact_id(artifact_id)
        session_code = self.get_context(
            self.get_node_by_id(artifact_id).session_id
        ).code

        nodes = [
            node
            for node in graph.nodes
            if node.lineno is not None and node.col_offset is not None
        ]

        # sort first by line number, then by column number
        nodes = sorted(nodes, key=lambda node: (node.lineno, node.col_offset))
        nodes = self.filter_subsumed_nodes(nodes)

        code = ""
        for node in nodes:
            node_code = Executor.get_segment_from_code(session_code, node)
            code += node_code + "\n"

        return code

    def find_all_artifacts_derived_from_data_source(
        self, program: Graph, data_source_node: DataSourceNode
    ) -> List[Node]:
        descendants = program.get_descendants(data_source_node)
        artifacts = []
        for d_id in descendants:
            artifact = (
                self.session.query(ArtifactORM).filter(ArtifactORM.id == d_id).first()
            )
            if artifact is not None:
                artifacts.append(program.get_node(d_id))
        return artifacts

    def gather_artifact_intermediate_nodes(self, program: Graph):
        """
        While this is on a single graph, it actually requires talking to the data asset manager, so didn't get put into the MetadataExtractor.
        """
