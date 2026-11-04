from PySide6.QtCore import Qt


def layout_fixed_cards(
    grid_layout,
    viewport_width,
    card_width,
    cards,
    previous_columns,
    max_columns=6,
):
    margins = grid_layout.contentsMargins()
    spacing = grid_layout.horizontalSpacing()
    available_width = viewport_width - margins.left() - margins.right()
    columns = min(
        max_columns,
        max(1, (available_width + spacing) // (card_width + spacing)),
    )

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
                _position_cards(grid_layout, cards, columns, card_width, spacing)
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
                grid_layout.activate()
                _position_cards(grid_layout, cards, columns, card_width, spacing)
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

    grid_layout.activate()
    _position_cards(grid_layout, cards, columns, card_width, spacing)
    return columns


def _position_cards(grid_layout, cards, columns, card_width, spacing):
    parent = grid_layout.parentWidget()
    margins = grid_layout.contentsMargins()
    available_width = parent.width() - margins.left() - margins.right()
    cell_width = (
        available_width - (columns - 1) * spacing
    ) // columns

    for index, card in enumerate(cards):
        column = index % columns
        row = index // columns
        x = (
            margins.left()
            + column * (cell_width + spacing)
            + max(0, (cell_width - card_width) // 2)
        )
        y = margins.top() + row * (card.height() + spacing)
        card.setGeometry(x, y, card_width, card.height())
