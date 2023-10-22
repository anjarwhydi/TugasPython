from http import HTTPStatus
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required
from app.logs.log import logger
from ..utils import db
from ..models.borrowing import Borrowing

borrowing_ns = Namespace('borrowings', description='Borrowing operations')

borrowing_model = borrowing_ns.model('Borrowing', {
    'id': fields.Integer(readOnly=True),
    'book_id': fields.Integer(required=True),
    'borrower_id': fields.Integer(required=True),
})

@borrowing_ns.route('')
class BorrowingListResource(Resource):
    @borrowing_ns.marshal_list_with(borrowing_model)
    @borrowing_ns.doc(responses={HTTPStatus.OK: 'Success'})
    @borrowing_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def get(self):
        try:
            borrowings = Borrowing.query.all()
            logger.info(f"Data: {borrowings}")
            return borrowings, HTTPStatus.OK
        except Exception as e:
            logger.info(f"Error: {e}")
            return {'message': 'Failed to retrieve borrowings', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @borrowing_ns.expect(borrowing_model, validate=True)
    @borrowing_ns.doc(responses={HTTPStatus.CREATED: 'Created', HTTPStatus.BAD_REQUEST: 'Invalid input'})
    @borrowing_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def post(self):
        try:
            data = request.json
            borrowing = Borrowing(book_id=data['book_id'], borrower_id=data['borrower_id'])
            db.session.add(borrowing)
            db.session.commit()
            logger.info(f"Data: {borrowing}")
            return {'message': 'Borrowing created successfully'}, HTTPStatus.CREATED
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to create borrowing', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

@borrowing_ns.route('/<int:id>')
class BorrowingResource(Resource):
    @borrowing_ns.marshal_with(borrowing_model)
    @borrowing_ns.doc(responses={HTTPStatus.OK: 'Success', HTTPStatus.NOT_FOUND: 'Borrowing not found'})
    @borrowing_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def get(self, id):
        try:
            borrowing = Borrowing.query.get_or_404(id)
            logger.info(f"Data: {borrowing}")
            return borrowing, HTTPStatus.OK
        except Exception as e:
            logger.info(f"Error: {e}")
            return {'message': 'Borrowing not found', 'error': str(e)}, HTTPStatus.NOT_FOUND
    
    @borrowing_ns.expect(borrowing_model)
    @borrowing_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def put(self, id):
        try:
            borrowing = Borrowing.query.get_or_404(id)
            data = request.json
            borrowing.book_id = data['book_id']
            borrowing.borrower_id = data['borrower_id']
            db.session.commit()
            logger.info(f"Data: {borrowing}")
            return {'message': 'Borrowing updated successfully'}, HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to update borrowing', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR

    @borrowing_ns.doc(responses={HTTPStatus.NO_CONTENT: 'No Content', HTTPStatus.NOT_FOUND: 'Borrowing not found'})
    @borrowing_ns.doc(params={'Authorization': {'in': 'header', 'description': 'Access Token'}})
    @jwt_required()
    def delete(self, id):
        try:
            borrowing = Borrowing.query.get_or_404(id)
            db.session.delete(borrowing)
            db.session.commit()
            logger.info(f"Data: {borrowing}")
            return {'message': 'Borrowing deleted successfully'}, HTTPStatus.NO_CONTENT
        except Exception as e:
            db.session.rollback()
            logger.info(f"Error: {e}")
            return {'message': 'Failed to delete borrowing', 'error': str(e)}, HTTPStatus.INTERNAL_SERVER_ERROR
