"""
Tests unitarios para las herramientas básicas del MCP
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from src.tools.basic_tools import register_tools


class TestBasicTools:
    """Tests para las herramientas básicas del MCP"""
    
    # Eliminado test_say_hello tras retirar la herramienta del registro
    

    def test_list_items(self):
        """Verifica la función list_items"""
        mock_mcp = MagicMock()
        register_tools(mock_mcp)
        
        # Verificar que se registró list_items
        tool_calls = [call for call in mock_mcp.tool.call_args_list]
        list_items_call = None
        for call in tool_calls:
            if 'list_items' in str(call):
                list_items_call = call
                break
        
        assert list_items_call is not None, "list_items no fue registrada"
    
    def test_health_tools_registration(self):
        """Verifica que se registren las herramientas de health check"""
        mock_mcp = MagicMock()
        register_tools(mock_mcp)
        
        # Verificar herramientas de health check
        tool_calls = [call for call in mock_mcp.tool.call_args_list]
        health_tools = [
            'health_readiness_check',
            'health_liveness_check', 
            'health_comprehensive_check'
        ]
        
        for tool_name in health_tools:
            tool_found = any(tool_name in str(call) for call in tool_calls)
            assert tool_found, f"{tool_name} no fue registrada"
    
    def test_audit_tools_registration(self):
        """Verifica que se registren las herramientas de auditoría"""
        mock_mcp = MagicMock()
        register_tools(mock_mcp)
        
        # Verificar herramientas de auditoría
        tool_calls = [call for call in mock_mcp.tool.call_args_list]
        audit_tools = [
            'audit_repo_run',
            'terminal_run_health_audit',
            'terminal_batch_health_check'
        ]
        
        for tool_name in audit_tools:
            tool_found = any(tool_name in str(call) for call in tool_calls)
            assert tool_found, f"{tool_name} no fue registrada"
    
    def test_terminal_tools_registration(self):
        """Verifica que se registren las herramientas de terminal"""
        mock_mcp = MagicMock()
        register_tools(mock_mcp)
        
        # Verificar herramientas de terminal
        tool_calls = [call for call in mock_mcp.tool.call_args_list]
        terminal_tools = [
            'terminal_execute_command',
            'terminal_health_check_service',
            'terminal_get_system_info'
        ]
        
        for tool_name in terminal_tools:
            tool_found = any(tool_name in str(call) for call in tool_calls)
            assert tool_found, f"{tool_name} no fue registrada"
    
    def test_all_tools_registered(self):
        """Verifica que todas las herramientas esperadas estén registradas"""
        mock_mcp = MagicMock()
        register_tools(mock_mcp)
        
        # Lista completa de herramientas esperadas (sin say_hello)
        expected_tools = [
            'list_items',
            'health_readiness_check',
            'health_liveness_check',
            'health_comprehensive_check',
            'audit_repo_run',
            'terminal_execute_command',
            'terminal_health_check_service',
            'terminal_run_health_audit',
            'terminal_batch_health_check',
            'terminal_get_system_info'
        ]
        
        # Verificar que se registraron todas
        tool_calls = [call for call in mock_mcp.tool.call_args_list]
        assert len(tool_calls) == len(expected_tools), f"Se esperaban {len(expected_tools)} herramientas, se registraron {len(tool_calls)}"
        
        for tool_name in expected_tools:
            tool_found = any(tool_name in str(call) for call in tool_calls)
            assert tool_found, f"{tool_name} no fue registrada"


class TestToolDecorators:
    """Tests para los decoradores de herramientas"""
    
    def test_tool_decorator_usage(self):
        """Verifica que se use el decorador @mcp.tool() correctamente"""
        mock_mcp = MagicMock()
        register_tools(mock_mcp)
        
        # Verificar que se llamó el decorador tool() para cada función
        tool_calls = mock_mcp.tool.call_args_list
        assert len(tool_calls) > 0, "No se registraron herramientas"
        
        # Verificar que cada llamada sea al decorador
        for call in tool_calls:
            assert call[0] == (), "El decorador tool() debe llamarse sin argumentos"
    
    def test_async_tools_registration(self):
        """Verifica que las herramientas asíncronas se registren correctamente"""
        mock_mcp = MagicMock()
        register_tools(mock_mcp)
        
        # Verificar herramientas asíncronas específicas
        async_tools = [
            'health_readiness_check',
            'health_liveness_check',
            'health_comprehensive_check',
            'audit_repo_run',
            'terminal_execute_command',
            'terminal_health_check_service',
            'terminal_run_health_audit',
            'terminal_batch_health_check',
            'terminal_get_system_info'
        ]
        
        tool_calls = [call for call in mock_mcp.tool.call_args_list]
        for tool_name in async_tools:
            tool_found = any(tool_name in str(call) for call in tool_calls)
            assert tool_found, f"Herramienta asíncrona {tool_name} no fue registrada"
    
    def test_sync_tools_registration(self):
        """Verifica que las herramientas síncronas se registren correctamente"""
        mock_mcp = MagicMock()
        register_tools(mock_mcp)
        
        # Verificar herramientas síncronas (sin say_hello)
        sync_tools = [
            'list_items'
        ]
        
        tool_calls = [call for call in mock_mcp.tool.call_args_list]
        for tool_name in sync_tools:
            tool_found = any(tool_name in str(call) for call in tool_calls)
            assert tool_found, f"Herramienta síncrona {tool_name} no fue registrada" 