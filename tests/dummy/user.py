from src.user.services import UserService, UserAuthService, UserEmailService


def create_test_user(user_service: UserService,
                     user_email_service: UserEmailService,
                     user_auth_service: UserAuthService):
    account = "test@gmail.com"
    password = "1q2w3e4r1!"
    res = user_service.create_user(account, password)
    code = user_email_service.send_join_verify_email(account)
    user_auth_service.join_verify(account, code)
    return res
