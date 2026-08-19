from app.services.platforms.gorgias_service import GorgiasService
# from app.services.platforms.zendesk_service import ZendeskService


def get_platform_service(client, db):

    if client.platform == "gorgias":
        credential = ...
        return GorgiasService(...)

    elif client.platform == "zendesk":
        credential = ...
        # return ZendeskService(...)

    else:
        raise Exception("Unsupported platform")