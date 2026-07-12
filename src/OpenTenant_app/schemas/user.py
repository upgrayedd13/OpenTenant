from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.user.user import User


class UserSchema:
    @staticmethod
    def parse_and_validate(data: dict) -> dict:
        if not isinstance(data, dict):
            raise ValueError('User data must be a dictionary')

        # Required fields
        required = ['username', 'email', 'password', 'name']
        for field in required:
            if field not in data or not data[field]:
                raise ValueError(f'Missing required user field: {field}')

        return {
            'username': str(data['username']).strip(),
            'email': str(data['email']).strip().lower(),
            'password': data['password'],
            'name': str(data['name']).strip(),
            'phone_number': data.get('phone_number'),
            'pronouns': data.get('pronouns'),
        }


    @classmethod
    def serialize(cls, user: 'User') -> dict:
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'name': user.name,
            'phone_number': user.phone_number,
            'pronouns': user.pronouns,
            'role': user.role,
        }
