from flask import Flask, request
from flask_restful import Api, Resource
from sqlalchemy import desc

from test_back_end import db
from test_back_end.models.cliente import Cliente as ClienteModel
from test_back_end.schemas.cliente import ClienteSchema

app = Flask(__name__)
api = Api(app)

STATUS_SUCCESS_200 = 200
STATUS_CREATED_SUCESS_201 = 201
STATUS_SUCCESS_NO_CONTENT_204 = 204


class ClienteResource(Resource):
    def get(self, cliente_id: int = None):
        """
        Retorna o cliente
        """

        if cliente_id is not None:
            cliente = ClienteModel.query.get_or_404(cliente_id).first()
            schema = ClienteSchema()
            json_cliente = schema.dumps(cliente)

        if cliente_id is None:
            # Ordenacao
            order_by = request.args.get("order_by")
            if order_by:
                if order_by[0] == "-":
                    query = ClienteModel.query.order_by(desc(order_by[1:]))
                else:
                    query = ClienteModel.query.order_by(order_by)
            else:
                query = ClienteModel.query.order_by("id")

            # Paginacao

            pagination_data = {
                "page": int,
                "per_page": int,
            }
            for key in pagination_data:
                if request.args.get(key) is not None:
                    pagination_data[key] = int(request.args.get(key))

            paginated_query = query.paginate(**pagination_data)
            # Fim
            cliente = paginated_query.items
            schema = ClienteSchema(many=True)
            json_cliente = schema.dumps(cliente)

        return json_cliente, STATUS_SUCCESS_200

    def put(self):
        """
        Adiciona um cliente
        """
        data = request.get_json()

        schema = ClienteSchema()
        validated_data = schema.load(data)

        cliente = ClienteModel(**validated_data)

        db.session.add(cliente)
        db.session.commit()

        return_data = schema.dumps(cliente)
        return return_data, STATUS_CREATED_SUCESS_201

    def delete(self, cliente_id):
        """
        Remove um cliente
        """
        cliente = ClienteModel.query.get_or_404(cliente_id)

        db.session.delete(cliente)
        db.session.commit()

        return {}, STATUS_SUCCESS_NO_CONTENT_204

    def patch(self, cliente_id):
        """
        Atualiza os dados de um cliente
        """
        cliente = ClienteModel.query.get_or_404(cliente_id)

        data = request.get_json()

        schema = ClienteSchema()
        validated_client_data = schema.load(data)

        # Atualiza os dados do Model com os dados recebidos
        for key, value in validated_client_data.items():
            setattr(cliente, key, value)

        db.session.commit()
        db.session.refresh(cliente)

        return_data = schema.dumps(cliente)
        return return_data, STATUS_SUCCESS_200
