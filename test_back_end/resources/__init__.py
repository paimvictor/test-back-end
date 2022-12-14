from flask import request
from flask_restful import Resource
from sqlalchemy import desc

from test_back_end import db

STATUS_SUCCESS_200 = 200
STATUS_CREATED_SUCESS_201 = 201
STATUS_SUCCESS_NO_CONTENT_204 = 204


class BaseCRUD:
    def __init__(self, model=None, schema=None):
        self.model = model
        self.schema = schema

    def _paginate(self, query):
        pagination_params = {
            "page": request.args.get("page", 1, type=int),
            "max_per_page": request.args.get("limit", None, type=int),
            "per_page": request.args.get("per_page", None, type=int),
        }
        # Remove keys with None values
        pagination_params = {
            k: v for k, v in pagination_params.items() if v is not None
        }

        paginated_result = query.paginate(**pagination_params)

        return paginated_result

    def _filter_by(self, query):
        columns_filter = {}
        columns_keys = query.statement.columns.keys()
        for column in columns_keys:
            columns_filter[column] = request.args.get(column, None, type=str)

        query = query.filter_by(**columns_filter)

        return query

    def _order_by(self, query):
        order_by = request.args.get("order_by", None, type=str)

        if not order_by:
            return query

        if order_by[0] == "-":
            order_by = order_by[1:]
            query = query.order_by(desc(order_by))
            return query
        else:
            query = query.order_by(order_by)
            return query

    def _get_query(
        self,
    ):
        query = self.model.query
        query = self._filter_by(query)
        query = self._order_by(query)
        query = self._paginate(query)
        return query

    def get(self, _id: int = None):
        """ """
        schema = self.schema()
        if _id is not None:
            result = self.model.query.get_or_404(_id).first()
            json_result = schema.dumps(result)

        if _id is None:
            paginated_result = self._get_query()
            schema = self.schema(many=True)
            json_result = schema.dumps(paginated_result.items)

        return json_result, STATUS_SUCCESS_200

    def put(self):
        """ """
        data = request.get_json()
        schema = self.schema()

        validated_data = schema.load(data)

        new_object = self.model(**validated_data)

        db.session.add(new_object)
        db.session.commit()

        return_data = schema.dumps(new_object)
        return return_data, STATUS_CREATED_SUCESS_201

    def delete(self, _id):
        """ """
        selected_object = self.model.query.get_or_404(_id)

        db.session.delete(selected_object)
        db.session.commit()

        return {}, STATUS_SUCCESS_NO_CONTENT_204

    def patch(self, _id):
        """ """
        selected_object = self.model.query.get_or_404(_id)

        data = request.get_json()

        schema = self.schema()
        validated_data = schema.load(data)

        # Atualiza os dados do Model com os dados recebidos
        for key, value in validated_data.items():
            setattr(selected_object, key, value)

        db.session.commit()
        db.session.refresh(selected_object)

        return_data = schema.dumps(selected_object)
        return return_data, STATUS_SUCCESS_200