from http import HTTPStatus
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from app.logs.log import logger
from ..utils import db
from ..models.borrower import Borrower

borrower_ns = Namespace('borrowers', description='Borrower operations')

borrower_model = borrower_ns.model('Borrower', {
    'id': fields.Integer(readOnly=True),
    'name': fields.String(required=True),
    'phone': fields.String(required=True),
})

@borrower_ns.route('')
class BorrowerListResource(Resource):
    @borrower_ns.marshal_list_with(borrower_model)
    @borrower_ns.doc(responses={HTTPStatus.OK: 'Success'})
    @borrower_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def get(self):
        try:
            borrowers = Borrower.query.all()
            logger.info(f"Data: {borrowers}")
            return borrowers, HTTPStatus.OK
        except Exception as e:
            logger.info(f"Error: {e}")
            return {'message': 'Failed to retrieve borrowers', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @borrower_ns.expect(borrower_model, validate=True)
    @borrower_ns.doc(responses={HTTPStatus.CREATED: 'Created', HTTPStatus.BAD_REQUEST: 'Invalid input'})
    @borrower_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def post(self):
        try:
            data = request.json
            borrower = Borrower(name=data['name'], phone=data['phone'])
            db.session.add(borrower)
            db.session.commit()
            logger.info(f"Data: {borrower}")
            return {'message': 'Borrower created successfully'}, HTTPStatus.CREATED
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to create borrower', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

@borrower_ns.route('/<int:id>')
class BorrowerResource(Resource):
    @borrower_ns.marshal_with(borrower_model)
    @borrower_ns.doc(responses={HTTPStatus.OK: 'Success', HTTPStatus.NOT_FOUND: 'Borrower not found'})
    @borrower_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def get(self, id):
        try:
            borrower = Borrower.query.get_or_404(id)
            logger.info(f"Data: {borrower}")
            return borrower, HTTPStatus.OK
        except Exception as e:
            logger.info(f"Error: {e}")
            return {'message': 'Borrower not found', 'error': str(e)}, HTTPStatus.NOT_FOUND
    
    @borrower_ns.expect(borrower_model)
    def put(self, id):
        try:
            borrower = Borrower.query.get_or_404(id)
            data = request.json
            borrower.name = data['name']
            borrower.phone = data['phone']
            db.session.commit()
            logger.info(f"Data: {borrower}")
            return {'message': 'Borrower updated successfully'}, HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to update borrower', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @borrower_ns.doc(responses={HTTPStatus.NO_CONTENT: 'No Content', HTTPStatus.NOT_FOUND: 'Borrower not found'})
    @borrower_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def delete(self, id):
        try:
            borrower = Borrower.query.get_or_404(id)
            db.session.delete(borrower)
            db.session.commit()
            logger.info(f"Data: {borrower}")
            return {'message': 'Borrower deleted successfully'}, HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to delete borrower', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
