from http import HTTPStatus
from flask import request
from flask_restx import Namespace, Resource, fields
from app.logs.log import logger
from flask_jwt_extended import jwt_required
from ..utils import db
from ..models.admin import Admin

admin_ns = Namespace('admins', description='Admin operations')

admin_model = admin_ns.model('Admin', {
    'id': fields.Integer(readOnly=True),
    'email': fields.String(required=True),
    'password': fields.String(required=True)
})

@admin_ns.route('')
class AdminListResource(Resource):
    @admin_ns.marshal_list_with(admin_model)
    @admin_ns.doc(responses={HTTPStatus.OK: 'Success'})
    @admin_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def get(self):
        try:
            admin = Admin.query.all()
            logger.info(f"Data: {admin}")
            return admin, HTTPStatus.OK
        except Exception as e:
            logger.info(f"Error: {e}")
            return {'message': 'Failed to retrieve Admins', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    # @admin_ns.expect(admin_model, validate=True)
    # @admin_ns.doc(responses={HTTPStatus.CREATED: 'Created', HTTPStatus.BAD_REQUEST: 'Invalid input'})
    # @admin_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    # @jwt_required()
    # def post(self):
    #     try:
    #         data = request.json
    #         admin = Admin(email=data['email'], password=data['password'])
    #         db.session.add(admin)
    #         db.session.commit()
    #         logger.info(f"Data: {admin}")
    #         return {'message': 'Admin created successfully'}, HTTPStatus.CREATED
    #     except Exception as e:
    #         db.session.rollback()
    #         logger.info(f"Error: {e}")
    #         return {'message': 'Failed to create Admin', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

@admin_ns.route('/<int:id>')
class AdminResource(Resource):
    @admin_ns.marshal_with(admin_model)
    @admin_ns.doc(responses={HTTPStatus.OK: 'Success', HTTPStatus.NOT_FOUND: 'Admin not found'})
    @admin_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def get(self, id):
        try:
            admin = Admin.query.get_or_404(id)
            logger.info(f"Data: {admin}")
            return admin, HTTPStatus.OK
        except Exception as e:
            logger.info(f"Error: {e}")
            return {'message': 'Admin not found', 'error': str(e)}, HTTPStatus.NOT_FOUND
    
    @admin_ns.expect(admin_model)
    def put(self, id):
        try:
            admin = Admin.query.get_or_404(id)
            data = request.json
            admin.email = data['email']
            admin.password = data['password']
            db.session.commit()
            logger.info(f"Data: {admin}")
            return {'message': 'Admin updated successfully'}, HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to update Admin', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @admin_ns.doc(responses={HTTPStatus.NO_CONTENT: 'No Content', HTTPStatus.NOT_FOUND: 'Admin not found'})
    @admin_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def delete(self, id):
        try:
            admin = Admin.query.get_or_404(id)
            db.session.delete(admin)
            db.session.commit()
            logger.info(f"Data: {admin}")
            return {'message': 'Admin deleted successfully'}, HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to delete Admin', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
