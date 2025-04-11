import graphene
import graphql_jwt

from .views import *

class Mutation(graphene.ObjectType):
    register_user = RegisterUser.Field()
    login_user = LoginUser.Field()
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()



class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, world!")

schema = graphene.Schema(query=Query, mutation=Mutation)