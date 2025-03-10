from __future__ import annotations

from types import TracebackType

try:
    from polars.polars import toggle_string_cache as pytoggle_string_cache

    _DOCUMENTING = False
except ImportError:
    _DOCUMENTING = True


class StringCache:
    """
    Context manager that allows data sources to share the same categorical features.
    This will temporarily cache the string categories until the context manager is
    finished.

    >>> with pl.StringCache():
    ...     df1 = pl.DataFrame(
    ...         [
    ...             pl.Series(
    ...                 "color", ["red", "green", "blue", "orange"], pl.Categorical
    ...             ),
    ...             pl.Series("uint8", [1, 2, 3, 4], pl.UInt8),
    ...         ]
    ...     )
    ...     df2 = pl.DataFrame(
    ...         [
    ...             pl.Series(
    ...                 "color",
    ...                 ["yellow", "green", "orange", "black", "red"],
    ...                 pl.Categorical,
    ...             ),
    ...             pl.Series("char", ["a", "b", "c", "d", "e"], pl.Utf8),
    ...         ]
    ...     )
    ...
    ...     # Both dataframes use the same string cache for the categorical column,
    ...     # so the join operation on that column will succeed.
    ...     df_join = df1.join(df2, how="inner", on="color")
    ...
    >>> df_join
    shape: (3, 3)
    ┌────────┬───────┬──────┐
    │ color  ┆ uint8 ┆ char │
    │ ---    ┆ ---   ┆ ---  │
    │ cat    ┆ u8    ┆ str  │
    ╞════════╪═══════╪══════╡
    │ green  ┆ 2     ┆ b    │
    ├╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌┤
    │ orange ┆ 4     ┆ c    │
    ├╌╌╌╌╌╌╌╌┼╌╌╌╌╌╌╌┼╌╌╌╌╌╌┤
    │ red    ┆ 1     ┆ e    │
    └────────┴───────┴──────┘
    """

    def __init__(self) -> None:
        pass

    def __enter__(self) -> StringCache:
        pytoggle_string_cache(True)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pytoggle_string_cache(False)


def toggle_string_cache(toggle: bool) -> None:
    """
    Turn on/off the global string cache. This ensures that casts to Categorical types
    have the categories when string values are equal.
    """
    pytoggle_string_cache(toggle)
