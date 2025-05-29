#!/bin/bash
# Script para monitoramento em tempo real dos logs do LinkedIn Bot

LOG_DIR="/var/log/linkedin"
LOCAL_LOG_DIR="logs"

# Detectar se está no Docker ou local
if [ -d "$LOG_DIR" ]; then
    MONITOR_DIR="$LOG_DIR"
    echo "🐳 Monitorando logs Docker: $LOG_DIR"
else
    MONITOR_DIR="$LOCAL_LOG_DIR"
    echo "💻 Monitorando logs locais: $LOCAL_LOG_DIR"
fi

# Verificar se diretório existe
if [ ! -d "$MONITOR_DIR" ]; then
    echo "❌ Diretório de logs não encontrado: $MONITOR_DIR"
    echo "💡 Execute primeiro:"
    if [ "$MONITOR_DIR" = "$LOG_DIR" ]; then
        echo "   sudo ./setup_logs.sh"
    else
        echo "   mkdir -p $LOCAL_LOG_DIR"
    fi
    exit 1
fi

# Função para mostrar menu
show_menu() {
    echo ""
    echo "📊 LinkedIn Bot - Monitor de Logs"
    echo "=================================="
    echo "1) 📄 Logs principais (poster.log)"
    echo "2) 📈 Logs CSV auditoria (linkedin_audit.csv)"
    echo "3) 🚨 Apenas erros"
    echo "4) 📸 Listar screenshots de falha"
    echo "5) 📊 Estatísticas CSV"
    echo "6) 🔍 Buscar por texto"
    echo "7) 🕐 Logs da última hora"
    echo "8) 📋 Ver status atual"
    echo "9) ❌ Sair"
    echo ""
    read -p "Escolha uma opção [1-9]: " choice
}

# Função para mostrar estatísticas CSV
show_csv_stats() {
    local csv_file="$MONITOR_DIR/linkedin_audit.csv"
    
    if [ ! -f "$csv_file" ]; then
        echo "❌ Arquivo CSV não encontrado: $csv_file"
        return
    fi
    
    echo "📊 Estatísticas de Auditoria:"
    echo "=============================="
    
    # Total de execuções
    total_lines=$(($(wc -l < "$csv_file") - 1))  # -1 para header
    echo "📈 Total de registros: $total_lines"
    
    # Sucessos vs Falhas
    if [ $total_lines -gt 0 ]; then
        successes=$(tail -n +2 "$csv_file" | cut -d',' -f4 | grep -c "True" || echo "0")
        failures=$(tail -n +2 "$csv_file" | cut -d',' -f4 | grep -c "False" || echo "0")
        
        echo "✅ Sucessos: $successes"
        echo "❌ Falhas: $failures"
        
        if [ $total_lines -gt 0 ]; then
            success_rate=$((successes * 100 / total_lines))
            echo "📊 Taxa de sucesso: ${success_rate}%"
        fi
        
        # Tipos de erro mais comuns
        echo ""
        echo "🚨 Top 5 erros mais comuns:"
        tail -n +2 "$csv_file" | cut -d',' -f7 | grep -v "^$" | sort | uniq -c | sort -nr | head -5 | while read count error; do
            echo "   $count × $error"
        done
        
        # Últimas execuções
        echo ""
        echo "🕐 Últimas 5 execuções:"
        tail -5 "$csv_file" | cut -d',' -f1,3,4 | while IFS=',' read timestamp action success; do
            if [ "$success" = "True" ]; then
                echo "   ✅ $timestamp - $action"
            else
                echo "   ❌ $timestamp - $action"
            fi
        done
    fi
}

# Loop principal
while true; do
    show_menu
    
    case $choice in
        1)
            echo "📄 Monitorando logs principais..."
            echo "   (Ctrl+C para parar)"
            tail -f "$MONITOR_DIR/poster.log" 2>/dev/null || echo "❌ Arquivo não encontrado"
            ;;
        2)
            echo "📈 Monitorando CSV auditoria..."
            echo "   (Ctrl+C para parar)"
            tail -f "$MONITOR_DIR/linkedin_audit.csv" 2>/dev/null || echo "❌ Arquivo não encontrado"
            ;;
        3)
            echo "🚨 Monitorando apenas erros..."
            echo "   (Ctrl+C para parar)"
            tail -f "$MONITOR_DIR/poster.log" 2>/dev/null | grep --line-buffered -E "(ERROR|❌|🚨)" || echo "❌ Arquivo não encontrado"
            ;;
        4)
            echo "📸 Screenshots de falha:"
            ls -la "$MONITOR_DIR"/fail_*.png 2>/dev/null | while read line; do
                echo "   $line"
            done || echo "   Nenhum screenshot encontrado"
            read -p "Pressione Enter para continuar..."
            ;;
        5)
            show_csv_stats
            read -p "Pressione Enter para continuar..."
            ;;
        6)
            read -p "🔍 Digite o texto para buscar: " search_term
            echo "Buscando '$search_term' nos logs..."
            grep -n "$search_term" "$MONITOR_DIR"/*.log 2>/dev/null || echo "Nenhum resultado encontrado"
            read -p "Pressione Enter para continuar..."
            ;;
        7)
            echo "🕐 Logs da última hora:"
            find "$MONITOR_DIR" -name "*.log" -newermt "1 hour ago" -exec tail -20 {} \; 2>/dev/null || echo "Nenhum log recente"
            read -p "Pressione Enter para continuar..."
            ;;
        8)
            echo "📋 Status atual:"
            echo "   📁 Diretório: $MONITOR_DIR"
            echo "   📊 Arquivos de log:"
            ls -la "$MONITOR_DIR"/*.{log,csv} 2>/dev/null | while read line; do
                echo "     $line"
            done || echo "     Nenhum arquivo encontrado"
            read -p "Pressione Enter para continuar..."
            ;;
        9)
            echo "👋 Saindo do monitor..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida. Tente novamente."
            sleep 1
            ;;
    esac
done 