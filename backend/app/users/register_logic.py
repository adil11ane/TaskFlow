import string
import secrets
from django.core.mail import send_mail
from django.core.cache import cache
from django.conf import settings



class RegistWithCodeFromEmailUseCase():
    def execute(self, email: str):
        generated_code = self._generate_code()
        # 3 send the code to email
        self._send_code_to_email(email, generated_code)
        # 4 save the code to cache with email as key
        cache.set(f"email_confirmation_code_{email}", generated_code, timeout=120)
        
    


    
    
    
    def _generate_code(self):
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
        return code
    
    def _send_code_to_email(self, email: str, code: str):
        send_mail(
            'Your confirmation code',
            f'Your confirmation code is {code}',
            settings.DEFAULT_FROM_EMAIL,
            [email],
        )
        