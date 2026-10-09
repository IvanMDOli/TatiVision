from PySide6.QtCore import Qt


def layout_fixed_cards(
    grid_layout,
    viewport_width,
    card_width,
    cards,
    previous_columns,
):
    margins = grid_layout.contentsMargins()
    spacing = grid_layout.horizontalSpacing()
    available_width = viewport_width - margins.left() - margins.right()
    columns = max(1, (available_width + spacing) // (card_width + spacing))

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
                        alignment=Qt.AlignCenter,
                    )
                return columns

    while grid_layout.count():
        grid_layout.takeAt(0)

    for index, card in enumerate(cards):
        grid_layout.addWidget(
            card,
            index // columns,
            index % columns,
            alignment=Qt.AlignCenter,
        )

    return columns
