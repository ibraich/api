from app.repositories.token_mention_repository import TokenMentionRepository


class TokenMentionService:
    __token_mention_repository: TokenMentionRepository

    def __init__(self, token_mention_repository):
        self.__token_mention_repository = token_mention_repository

    def create_token_mention(self, token_id, mention_id):
        return self.__token_mention_repository.create_token_mention(
            token_id, mention_id
        )

    def get_token_mention(self, token_ids, mention_ids):
        return self.__token_mention_repository.get_token_mention(token_ids, mention_ids)

    def get_token_mentions_by_mention_id(self, mention_id):
        return self.__token_mention_repository.get_token_mentions_by_mention_id(mention_id)

    def delete_token_mentions_by_mention_id(self, mention_id):
        token_mentions = self.get_token_mentions_by_mention_id(mention_id)
        for token_mention in token_mentions:
            self.__token_mention_repository.delete_token_mention_by_id(token_mention.id)


token_mention_service = TokenMentionService(TokenMentionRepository())
