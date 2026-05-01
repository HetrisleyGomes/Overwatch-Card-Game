class ProgressController:
    def __init__(self, repository):
        self.__repository = repository

    def set_card(self, user_id, card_id):
        try:
            self.__repository.set_card(user_id, card_id)
        except Exception as e:
            return str(e)
    
    def get_all_cards_id(self, user_id):
        try:
            data = self.__repository.get_all_cards_id(user_id)
            return data
        except Exception as e:
            return str(e)
        
    def get_all_sets(self, user_id):
        try:
            data = self.__repository.get_all_sets(user_id)
            return data
        except Exception as e:
            return str(e)
        
    def set_set(self, user_id, set_id):
        try:
            self.__repository.set_set(user_id, set_id)
        except Exception as e:
            return str(e)


    def get_deck(self, user_id):
        return self.__repository.get_deck(user_id)

    def set_deck(self, user_id, deck_novo):
        self.__repository.clear_deck(user_id)

        for card_id in deck_novo:
            self.__repository.add_card_to_deck(user_id, card_id)

    
    def get_user_icons(self, user_id):
        try:
            data = self.__repository.get_user_icons(user_id)
            return data
        except Exception as e:
            return str(e)
        
    def set_icon(self, user_id, icon_id):
        try:
            self.__repository.set_icon(user_id, icon_id)
        except Exception as e:
            return str(e)
    
    def get_user_prom(self, user_id):
        try:
            data = self.__repository.get_user_prom(user_id)
            return data
        except Exception as e:
            return str(e)
    
    def buy_big_pack(self, user_id, pacotaco_id):
        try:
            self.__repository.set_user_prom(user_id, pacotaco_id)
        except Exception as e:
            return str(e)