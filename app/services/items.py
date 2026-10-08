from app.schemas.item import Item, ItemCreate, ItemUpdate


class ItemNotFoundError(Exception):
    def __init__(self, item_id: int):
        self.item_id = item_id
        super().__init__(f"Item {item_id} not found")


class ItemService:
    def __init__(self) -> None:
        self._items: dict[int, Item] = {}
        self._next_id = 1

    def list_items(self) -> list[Item]:
        return list(self._items.values())

    def get_item(self, item_id: int) -> Item:
        item = self._items.get(item_id)
        if item is None:
            raise ItemNotFoundError(item_id)
        return item

    def create_item(self, payload: ItemCreate) -> Item:
        item = Item(id=self._next_id, **payload.model_dump())
        self._items[item.id] = item
        self._next_id += 1
        return item

    def update_item(self, item_id: int, payload: ItemUpdate) -> Item:
        item = self.get_item(item_id)
        updated = item.model_copy(update=payload.model_dump(exclude_unset=True))
        self._items[item_id] = updated
        return updated

    def delete_item(self, item_id: int) -> None:
        self.get_item(item_id)
        del self._items[item_id]


item_service = ItemService()
