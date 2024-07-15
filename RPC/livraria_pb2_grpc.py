# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc
import warnings

import livraria_pb2 as livraria__pb2

GRPC_GENERATED_VERSION = '1.64.1'
GRPC_VERSION = grpc.__version__
EXPECTED_ERROR_RELEASE = '1.65.0'
SCHEDULED_RELEASE_DATE = 'June 25, 2024'
_version_not_supported = False

try:
    from grpc._utilities import first_version_is_lower
    _version_not_supported = first_version_is_lower(GRPC_VERSION, GRPC_GENERATED_VERSION)
except ImportError:
    _version_not_supported = True

if _version_not_supported:
    warnings.warn(
        f'The grpc package installed is at version {GRPC_VERSION},'
        + f' but the generated code in livraria_pb2_grpc.py depends on'
        + f' grpcio>={GRPC_GENERATED_VERSION}.'
        + f' Please upgrade your grpc module to grpcio>={GRPC_GENERATED_VERSION}'
        + f' or downgrade your generated code using grpcio-tools<={GRPC_VERSION}.'
        + f' This warning will become an error in {EXPECTED_ERROR_RELEASE},'
        + f' scheduled for release on {SCHEDULED_RELEASE_DATE}.',
        RuntimeWarning
    )


class LivrariaStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.Cadastrar = channel.unary_unary(
                '/livraria.Livraria/Cadastrar',
                request_serializer=livraria__pb2.Usuario.SerializeToString,
                response_deserializer=livraria__pb2.Resposta.FromString,
                _registered_method=True)
        self.Login = channel.unary_unary(
                '/livraria.Livraria/Login',
                request_serializer=livraria__pb2.Usuario.SerializeToString,
                response_deserializer=livraria__pb2.Resposta.FromString,
                _registered_method=True)
        self.AdicionarLivro = channel.unary_unary(
                '/livraria.Livraria/AdicionarLivro',
                request_serializer=livraria__pb2.Livro.SerializeToString,
                response_deserializer=livraria__pb2.Resposta.FromString,
                _registered_method=True)
        self.Listar = channel.unary_unary(
                '/livraria.Livraria/Listar',
                request_serializer=livraria__pb2.Index.SerializeToString,
                response_deserializer=livraria__pb2.Livro.FromString,
                _registered_method=True)
        self.Iniciar = channel.unary_unary(
                '/livraria.Livraria/Iniciar',
                request_serializer=livraria__pb2.Index.SerializeToString,
                response_deserializer=livraria__pb2.Resposta.FromString,
                _registered_method=True)
        self.Pedir = channel.unary_unary(
                '/livraria.Livraria/Pedir',
                request_serializer=livraria__pb2.Pedido.SerializeToString,
                response_deserializer=livraria__pb2.Resposta.FromString,
                _registered_method=True)
        self.Pedidos = channel.unary_unary(
                '/livraria.Livraria/Pedidos',
                request_serializer=livraria__pb2.Index.SerializeToString,
                response_deserializer=livraria__pb2.Pedido.FromString,
                _registered_method=True)


class LivrariaServicer(object):
    """Missing associated documentation comment in .proto file."""

    def Cadastrar(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Login(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def AdicionarLivro(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Listar(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Iniciar(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Pedir(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def Pedidos(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_LivrariaServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'Cadastrar': grpc.unary_unary_rpc_method_handler(
                    servicer.Cadastrar,
                    request_deserializer=livraria__pb2.Usuario.FromString,
                    response_serializer=livraria__pb2.Resposta.SerializeToString,
            ),
            'Login': grpc.unary_unary_rpc_method_handler(
                    servicer.Login,
                    request_deserializer=livraria__pb2.Usuario.FromString,
                    response_serializer=livraria__pb2.Resposta.SerializeToString,
            ),
            'AdicionarLivro': grpc.unary_unary_rpc_method_handler(
                    servicer.AdicionarLivro,
                    request_deserializer=livraria__pb2.Livro.FromString,
                    response_serializer=livraria__pb2.Resposta.SerializeToString,
            ),
            'Listar': grpc.unary_unary_rpc_method_handler(
                    servicer.Listar,
                    request_deserializer=livraria__pb2.Index.FromString,
                    response_serializer=livraria__pb2.Livro.SerializeToString,
            ),
            'Iniciar': grpc.unary_unary_rpc_method_handler(
                    servicer.Iniciar,
                    request_deserializer=livraria__pb2.Index.FromString,
                    response_serializer=livraria__pb2.Resposta.SerializeToString,
            ),
            'Pedir': grpc.unary_unary_rpc_method_handler(
                    servicer.Pedir,
                    request_deserializer=livraria__pb2.Pedido.FromString,
                    response_serializer=livraria__pb2.Resposta.SerializeToString,
            ),
            'Pedidos': grpc.unary_unary_rpc_method_handler(
                    servicer.Pedidos,
                    request_deserializer=livraria__pb2.Index.FromString,
                    response_serializer=livraria__pb2.Pedido.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'livraria.Livraria', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))
    server.add_registered_method_handlers('livraria.Livraria', rpc_method_handlers)


 # This class is part of an EXPERIMENTAL API.
class Livraria(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def Cadastrar(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livraria.Livraria/Cadastrar',
            livraria__pb2.Usuario.SerializeToString,
            livraria__pb2.Resposta.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Login(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livraria.Livraria/Login',
            livraria__pb2.Usuario.SerializeToString,
            livraria__pb2.Resposta.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def AdicionarLivro(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livraria.Livraria/AdicionarLivro',
            livraria__pb2.Livro.SerializeToString,
            livraria__pb2.Resposta.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Listar(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livraria.Livraria/Listar',
            livraria__pb2.Index.SerializeToString,
            livraria__pb2.Livro.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Iniciar(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livraria.Livraria/Iniciar',
            livraria__pb2.Index.SerializeToString,
            livraria__pb2.Resposta.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Pedir(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livraria.Livraria/Pedir',
            livraria__pb2.Pedido.SerializeToString,
            livraria__pb2.Resposta.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)

    @staticmethod
    def Pedidos(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(
            request,
            target,
            '/livraria.Livraria/Pedidos',
            livraria__pb2.Index.SerializeToString,
            livraria__pb2.Pedido.FromString,
            options,
            channel_credentials,
            insecure,
            call_credentials,
            compression,
            wait_for_ready,
            timeout,
            metadata,
            _registered_method=True)
