from http import HTTPStatus
from flask import request, current_app
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, create_access_token, create_refresh_token, get_jwt_identity
from app.logs.log import logger

from ..utils import db
from ..utils.utils import checkUserEmailExist
from ..models.admin import Admin

auth_ns = Namespace('auth', description='Namespace for authentication')

register_model = auth_ns.model(
    'RegisterInput', {
        'email': fields.String(),
        'password': fields.String()
    }
)

login_model = auth_ns.model(
    'LoginInput', {
        'email': fields.String(),
        'password': fields.String()
    }
)

register_output_model = auth_ns.model(
    'RegisterOutput', {
        'email': fields.String(),
        'access_token': fields.String(),
        'refresh_token': fields.String()
    }
)

refresh_input_model = auth_ns.model(
    'RefreshInput', {
        'refresh_token': fields.String()
    }
)

@auth_ns.route('/signup')
class SignUp(Resource):
    @auth_ns.expect(register_model)
    @auth_ns.marshal_with(register_output_model)
    def post(self):
        data = request.json
        bcrypt = current_app.extensions['bcrypt']

        if checkUserEmailExist(data.get('email')):
            auth_ns.abort(HTTPStatus.BAD_REQUEST, message="Email is already taken.")

        input = Admin(
            email=data['email'],
            password=bcrypt.generate_password_hash(data['password']).decode('utf-8'),
        )

        try:
            db.session.add(input)
            db.session.commit()
            logger.info(f"Data: {input}")
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to register user', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

        access_token = create_access_token(identity=input.email)
        refresh_token = create_refresh_token(identity=input.email)

        return {'email': input.email, 'access_token': access_token, 'refresh_token': refresh_token}, HTTPStatus.CREATED

@auth_ns.route('/login')
class Login(Resource):
    @auth_ns.expect(login_model)
    def post(self):
        data = request.json
        bcrypt = current_app.extensions['bcrypt']

        user = Admin.query.filter_by(email=data['email']).first()

        if not user:
            auth_ns.abort(HTTPStatus.BAD_REQUEST, message="Email is not found.")

        checkPassword = bcrypt.check_password_hash(user.password, data['password'])

        if not checkPassword:
            auth_ns.abort(HTTPStatus.BAD_REQUEST, message="Password is incorrect.")

        access_token = create_access_token(identity=user.email)
        refresh_token = create_refresh_token(identity=user.email)
        logger.info(f"Data: {data}")
        return {'access_token': access_token, 'refresh_token': refresh_token}, HTTPStatus.CREATED

@auth_ns.route('/refresh')
class Refresh(Resource):
    @auth_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @auth_ns.expect(refresh_input_model)
    @jwt_required(refresh=True)
    def post(self):
        data = request.json
        email = get_jwt_identity()

        access_token = create_access_token(identity=email, fresh=True)
        logger.info(f"Data: {data}")
        return {'access_token': access_token, 'refresh_token': data['refresh_token']}, HTTPStatus.CREATED
