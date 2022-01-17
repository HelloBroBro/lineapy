import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
import pandas as pd
df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
df.to_parquet("test.parquet", index=False)
df2 = pd.read_parquet("test.parquet")

lineapy.save(df2, \'df2\')
""",
    location=PosixPath("[source file path]"),
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=19,
        source_code=source_1.id,
    ),
    library=Library(
        name="pandas",
    ),
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=24,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=7,
            col_offset=0,
            end_lineno=7,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            ImportNode(
                source_location=SourceLocation(
                    lineno=1,
                    col_offset=0,
                    end_lineno=1,
                    end_col_offset=14,
                    source_code=source_1.id,
                ),
                library=Library(
                    name="lineapy",
                ),
            ).id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=6,
                end_lineno=5,
                end_col_offset=37,
                source_code=source_1.id,
            ),
            function_id=CallNode(
                source_location=SourceLocation(
                    lineno=5,
                    col_offset=6,
                    end_lineno=5,
                    end_col_offset=21,
                    source_code=source_1.id,
                ),
                function_id=LookupNode(
                    name="getattr",
                ).id,
                positional_args=[
                    import_2.id,
                    LiteralNode(
                        value="read_parquet",
                    ).id,
                ],
            ).id,
            positional_args=[
                LiteralNode(
                    source_location=SourceLocation(
                        lineno=5,
                        col_offset=22,
                        end_lineno=5,
                        end_col_offset=36,
                        source_code=source_1.id,
                    ),
                    value="test.parquet",
                ).id
            ],
            implicit_dependencies=[
                MutateNode(
                    source_id=LookupNode(
                        name="file_system",
                    ).id,
                    call_id=CallNode(
                        source_location=SourceLocation(
                            lineno=4,
                            col_offset=0,
                            end_lineno=4,
                            end_col_offset=42,
                            source_code=source_1.id,
                        ),
                        function_id=CallNode(
                            source_location=SourceLocation(
                                lineno=4,
                                col_offset=0,
                                end_lineno=4,
                                end_col_offset=13,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="getattr",
                            ).id,
                            positional_args=[
                                CallNode(
                                    source_location=SourceLocation(
                                        lineno=3,
                                        col_offset=5,
                                        end_lineno=3,
                                        end_col_offset=51,
                                        source_code=source_1.id,
                                    ),
                                    function_id=CallNode(
                                        source_location=SourceLocation(
                                            lineno=3,
                                            col_offset=5,
                                            end_lineno=3,
                                            end_col_offset=17,
                                            source_code=source_1.id,
                                        ),
                                        function_id=LookupNode(
                                            name="getattr",
                                        ).id,
                                        positional_args=[
                                            import_2.id,
                                            LiteralNode(
                                                value="DataFrame",
                                            ).id,
                                        ],
                                    ).id,
                                    positional_args=[
                                        CallNode(
                                            source_location=SourceLocation(
                                                lineno=3,
                                                col_offset=18,
                                                end_lineno=3,
                                                end_col_offset=50,
                                                source_code=source_1.id,
                                            ),
                                            function_id=LookupNode(
                                                name="l_dict",
                                            ).id,
                                            positional_args=[
                                                CallNode(
                                                    function_id=LookupNode(
                                                        name="l_tuple",
                                                    ).id,
                                                    positional_args=[
                                                        LiteralNode(
                                                            source_location=SourceLocation(
                                                                lineno=3,
                                                                col_offset=19,
                                                                end_lineno=3,
                                                                end_col_offset=22,
                                                                source_code=source_1.id,
                                                            ),
                                                            value="a",
                                                        ).id,
                                                        CallNode(
                                                            source_location=SourceLocation(
                                                                lineno=3,
                                                                col_offset=24,
                                                                end_lineno=3,
                                                                end_col_offset=33,
                                                                source_code=source_1.id,
                                                            ),
                                                            function_id=LookupNode(
                                                                name="l_list",
                                                            ).id,
                                                            positional_args=[
                                                                LiteralNode(
                                                                    source_location=SourceLocation(
                                                                        lineno=3,
                                                                        col_offset=25,
                                                                        end_lineno=3,
                                                                        end_col_offset=26,
                                                                        source_code=source_1.id,
                                                                    ),
                                                                    value=1,
                                                                ).id,
                                                                LiteralNode(
                                                                    source_location=SourceLocation(
                                                                        lineno=3,
                                                                        col_offset=28,
                                                                        end_lineno=3,
                                                                        end_col_offset=29,
                                                                        source_code=source_1.id,
                                                                    ),
                                                                    value=2,
                                                                ).id,
                                                                LiteralNode(
                                                                    source_location=SourceLocation(
                                                                        lineno=3,
                                                                        col_offset=31,
                                                                        end_lineno=3,
                                                                        end_col_offset=32,
                                                                        source_code=source_1.id,
                                                                    ),
                                                                    value=3,
                                                                ).id,
                                                            ],
                                                        ).id,
                                                    ],
                                                ).id,
                                                CallNode(
                                                    function_id=LookupNode(
                                                        name="l_tuple",
                                                    ).id,
                                                    positional_args=[
                                                        LiteralNode(
                                                            source_location=SourceLocation(
                                                                lineno=3,
                                                                col_offset=35,
                                                                end_lineno=3,
                                                                end_col_offset=38,
                                                                source_code=source_1.id,
                                                            ),
                                                            value="b",
                                                        ).id,
                                                        CallNode(
                                                            source_location=SourceLocation(
                                                                lineno=3,
                                                                col_offset=40,
                                                                end_lineno=3,
                                                                end_col_offset=49,
                                                                source_code=source_1.id,
                                                            ),
                                                            function_id=LookupNode(
                                                                name="l_list",
                                                            ).id,
                                                            positional_args=[
                                                                LiteralNode(
                                                                    source_location=SourceLocation(
                                                                        lineno=3,
                                                                        col_offset=41,
                                                                        end_lineno=3,
                                                                        end_col_offset=42,
                                                                        source_code=source_1.id,
                                                                    ),
                                                                    value=4,
                                                                ).id,
                                                                LiteralNode(
                                                                    source_location=SourceLocation(
                                                                        lineno=3,
                                                                        col_offset=44,
                                                                        end_lineno=3,
                                                                        end_col_offset=45,
                                                                        source_code=source_1.id,
                                                                    ),
                                                                    value=5,
                                                                ).id,
                                                                LiteralNode(
                                                                    source_location=SourceLocation(
                                                                        lineno=3,
                                                                        col_offset=47,
                                                                        end_lineno=3,
                                                                        end_col_offset=48,
                                                                        source_code=source_1.id,
                                                                    ),
                                                                    value=6,
                                                                ).id,
                                                            ],
                                                        ).id,
                                                    ],
                                                ).id,
                                            ],
                                        ).id
                                    ],
                                ).id,
                                LiteralNode(
                                    value="to_parquet",
                                ).id,
                            ],
                        ).id,
                        positional_args=[
                            LiteralNode(
                                source_location=SourceLocation(
                                    lineno=4,
                                    col_offset=14,
                                    end_lineno=4,
                                    end_col_offset=28,
                                    source_code=source_1.id,
                                ),
                                value="test.parquet",
                            ).id
                        ],
                        keyword_args={
                            "index": LiteralNode(
                                source_location=SourceLocation(
                                    lineno=4,
                                    col_offset=36,
                                    end_lineno=4,
                                    end_col_offset=41,
                                    source_code=source_1.id,
                                ),
                                value=False,
                            ).id
                        },
                    ).id,
                ).id
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=18,
                end_lineno=7,
                end_col_offset=23,
                source_code=source_1.id,
            ),
            value="df2",
        ).id,
    ],
)
