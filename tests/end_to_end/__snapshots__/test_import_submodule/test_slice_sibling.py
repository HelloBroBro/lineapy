import datetime
from pathlib import *
from lineapy.data.types import *
from lineapy.utils.utils import get_new_id

source_1 = SourceCode(
    code="""import lineapy
import import_data.utils.__no_imported_submodule
import import_data.utils.__no_imported_submodule_prime
first_is_prime = import_data.utils.__no_imported_submodule.is_prime
second_is_prime = import_data.utils.__no_imported_submodule_prime.is_prime

lineapy.save(first_is_prime, \'first_is_prime\')
lineapy.save(second_is_prime, \'second_is_prime\')
""",
    location=PosixPath("[source file path]"),
)
call_1 = CallNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="lineapy",
        ).id
    ],
)
import_1 = ImportNode(
    source_location=SourceLocation(
        lineno=1,
        col_offset=0,
        end_lineno=1,
        end_col_offset=14,
        source_code=source_1.id,
    ),
    name="lineapy",
    version="",
    package_name="lineapy",
)
call_2 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="import_data",
        ).id
    ],
)
call_3 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="utils",
        ).id,
        call_2.id,
    ],
)
import_2 = ImportNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    name="import_data.utils.__no_imported_submodule",
    version="",
    package_name="import_data",
)
call_4 = CallNode(
    source_location=SourceLocation(
        lineno=2,
        col_offset=0,
        end_lineno=2,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="__no_imported_submodule",
        ).id,
        call_3.id,
    ],
)
mutate_2 = MutateNode(
    source_id=call_3.id,
    call_id=call_4.id,
)
call_5 = CallNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=54,
        source_code=source_1.id,
    ),
    function_id=LookupNode(
        name="l_import",
    ).id,
    positional_args=[
        LiteralNode(
            value="__no_imported_submodule_prime",
        ).id,
        mutate_2.id,
    ],
)
mutate_4 = MutateNode(
    source_id=call_4.id,
    call_id=call_5.id,
)
mutate_5 = MutateNode(
    source_id=mutate_2.id,
    call_id=call_5.id,
)
mutate_6 = MutateNode(
    source_id=MutateNode(
        source_id=MutateNode(
            source_id=call_2.id,
            call_id=call_3.id,
        ).id,
        call_id=call_4.id,
    ).id,
    call_id=call_5.id,
)
import_3 = ImportNode(
    source_location=SourceLocation(
        lineno=3,
        col_offset=0,
        end_lineno=3,
        end_col_offset=54,
        source_code=source_1.id,
    ),
    name="import_data.utils.__no_imported_submodule_prime",
    version="",
    package_name="import_data",
)
call_13 = CallNode(
    source_location=SourceLocation(
        lineno=7,
        col_offset=0,
        end_lineno=7,
        end_col_offset=46,
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
            call_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=4,
                col_offset=17,
                end_lineno=4,
                end_col_offset=67,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=4,
                        col_offset=17,
                        end_lineno=4,
                        end_col_offset=58,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="getattr",
                    ).id,
                    positional_args=[
                        CallNode(
                            source_location=SourceLocation(
                                lineno=4,
                                col_offset=17,
                                end_lineno=4,
                                end_col_offset=34,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="getattr",
                            ).id,
                            positional_args=[
                                mutate_6.id,
                                LiteralNode(
                                    value="utils",
                                ).id,
                            ],
                        ).id,
                        LiteralNode(
                            value="__no_imported_submodule",
                        ).id,
                    ],
                ).id,
                LiteralNode(
                    value="is_prime",
                ).id,
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=7,
                col_offset=29,
                end_lineno=7,
                end_col_offset=45,
                source_code=source_1.id,
            ),
            value="first_is_prime",
        ).id,
    ],
)
call_15 = CallNode(
    source_location=SourceLocation(
        lineno=8,
        col_offset=0,
        end_lineno=8,
        end_col_offset=48,
        source_code=source_1.id,
    ),
    function_id=CallNode(
        source_location=SourceLocation(
            lineno=8,
            col_offset=0,
            end_lineno=8,
            end_col_offset=12,
            source_code=source_1.id,
        ),
        function_id=LookupNode(
            name="getattr",
        ).id,
        positional_args=[
            call_1.id,
            LiteralNode(
                value="save",
            ).id,
        ],
    ).id,
    positional_args=[
        CallNode(
            source_location=SourceLocation(
                lineno=5,
                col_offset=18,
                end_lineno=5,
                end_col_offset=74,
                source_code=source_1.id,
            ),
            function_id=LookupNode(
                name="getattr",
            ).id,
            positional_args=[
                CallNode(
                    source_location=SourceLocation(
                        lineno=5,
                        col_offset=18,
                        end_lineno=5,
                        end_col_offset=65,
                        source_code=source_1.id,
                    ),
                    function_id=LookupNode(
                        name="getattr",
                    ).id,
                    positional_args=[
                        CallNode(
                            source_location=SourceLocation(
                                lineno=5,
                                col_offset=18,
                                end_lineno=5,
                                end_col_offset=35,
                                source_code=source_1.id,
                            ),
                            function_id=LookupNode(
                                name="getattr",
                            ).id,
                            positional_args=[
                                mutate_6.id,
                                LiteralNode(
                                    value="utils",
                                ).id,
                            ],
                        ).id,
                        LiteralNode(
                            value="__no_imported_submodule_prime",
                        ).id,
                    ],
                ).id,
                LiteralNode(
                    value="is_prime",
                ).id,
            ],
        ).id,
        LiteralNode(
            source_location=SourceLocation(
                lineno=8,
                col_offset=30,
                end_lineno=8,
                end_col_offset=47,
                source_code=source_1.id,
            ),
            value="second_is_prime",
        ).id,
    ],
)