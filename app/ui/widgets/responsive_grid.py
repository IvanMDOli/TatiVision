from PySide6.QtCore import Qt


def layout_fixed_cards(
    grid_layout,
    viewport_width,
    card_width,
    cards,
    previous_columns,
    max_columns=6,
    spread=False,
):
    grid_layout.setAlignment(Qt.AlignLeft | Qt.AlignTop)
    margins = grid_layout.contentsMargins()
    spacing = grid_layout.horizontalSpacing()
    available_width = viewport_width - margins.left() - margins.right()
    max_fitting_columns = max(
        1,
        (available_width + spacing) // (card_width + spacing),
    )
    columns = min(
        max_columns,
        max_fitting_columns,
        max_columns if spread else max(1, len(cards)),
    )

    if spread and columns > 1:
        spacing = max(
            spacing,
            (available_width - columns * card_width) // (columns - 1),
        )
        grid_layout.setHorizontalSpacing(spacing)
        for column in range(max_columns):
            grid_layout.setColumnMinimumWidth(
                column,
                card_width if column < columns else 0,
            )
    else:
        for column in range(max_columns):
            grid_layout.setColumnMinimumWidth(column, 0)

    if columns == previous_columns and grid_layout.count():
        existing_count = grid_layout.count()
        if existing_count == len(cards):
            positions = [
                grid_layout.getItemPosition(index)[:2]
                for index in range(existing_count)
            ]
            expected = [
                (index // columns, index % columns)
                for index in range(existing_count)
            ]
            if positions == expected:
                grid_layout.activate()
                return columns
        elif existing_count < len(cards):
            positions = [
                grid_layout.getItemPosition(index)[:2]
                for index in range(existing_count)
            ]
            expected = [
                (index // columns, index % columns)
                for index in range(existing_count)
            ]
            if positions == expected:
                for index in range(existing_count, len(cards)):
                    grid_layout.addWidget(
                        cards[index],
                        index // columns,
                        index % columns,
                        alignment=Qt.AlignLeft | Qt.AlignTop,
                    )
                grid_layout.activate()
                return columns

    while grid_layout.count():
        grid_layout.takeAt(0)

    for index, card in enumerate(cards):
        grid_layout.addWidget(
            card,
            index // columns,
            index % columns,
            alignment=Qt.AlignLeft | Qt.AlignTop,
        )

    grid_layout.activate()
    return columns
