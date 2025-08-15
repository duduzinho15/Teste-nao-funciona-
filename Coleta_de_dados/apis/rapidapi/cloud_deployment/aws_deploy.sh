#!/bin/bash

# Script de Deploy para AWS - FASE 3
# Sistema de Produção RapidAPI com ML e Prometheus

set -e

# Configurações
CLUSTER_NAME="rapidapi-production"
REGION="us-east-1"
VPC_CIDR="10.0.0.0/16"
SUBNET_CIDR="10.0.1.0/24"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Iniciando Deploy AWS para RapidAPI - FASE 3${NC}"
echo "=================================================="

# Verifica dependências
check_dependencies() {
    echo -e "${YELLOW}📋 Verificando dependências...${NC}"
    
    command -v aws >/dev/null 2>&1 || { echo -e "${RED}❌ AWS CLI não encontrado${NC}"; exit 1; }
    command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}❌ kubectl não encontrado${NC}"; exit 1; }
    command -v eksctl >/dev/null 2>&1 || { echo -e "${RED}❌ eksctl não encontrado${NC}"; exit 1; }
    command -v helm >/dev/null 2>&1 || { echo -v "${RED}❌ Helm não encontrado${NC}"; exit 1; }
    
    echo -e "${GREEN}✅ Todas as dependências estão instaladas${NC}"
}

# Configura AWS
setup_aws() {
    echo -e "${YELLOW}🔧 Configurando AWS...${NC}"
    
    # Configura região padrão
    aws configure set default.region $REGION
    
    # Verifica se está logado
    if ! aws sts get-caller-identity >/dev/null 2>&1; then
        echo -e "${RED}❌ Não está logado na AWS. Execute 'aws configure' primeiro.${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ AWS configurado para região: $REGION${NC}"
}

# Cria VPC e infraestrutura de rede
create_network() {
    echo -e "${YELLOW}🌐 Criando infraestrutura de rede...${NC}"
    
    # Cria VPC
    VPC_ID=$(aws ec2 create-vpc \
        --cidr-block $VPC_CIDR \
        --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=rapidapi-vpc}]' \
        --query 'Vpc.VpcId' \
        --output text)
    
    echo -e "${GREEN}✅ VPC criada: $VPC_ID${NC}"
    
    # Cria Internet Gateway
    IGW_ID=$(aws ec2 create-internet-gateway \
        --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=rapidapi-igw}]' \
        --query 'InternetGateway.InternetGatewayId' \
        --output text)
    
    # Anexa Internet Gateway à VPC
    aws ec2 attach-internet-gateway \
        --vpc-id $VPC_ID \
        --internet-gateway-id $IGW_ID
    
    echo -e "${GREEN}✅ Internet Gateway criado e anexado${NC}"
    
    # Cria subnets
    SUBNET_ID=$(aws ec2 create-subnet \
        --vpc-id $VPC_ID \
        --cidr-block $SUBNET_CIDR \
        --availability-zone ${REGION}a \
        --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=rapidapi-subnet}]' \
        --query 'Subnet.SubnetId' \
        --output text)
    
    echo -e "${GREEN}✅ Subnet criada: $SUBNET_ID${NC}"
    
    # Cria Route Table
    ROUTE_TABLE_ID=$(aws ec2 create-route-table \
        --vpc-id $VPC_ID \
        --tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=rapidapi-rt}]' \
        --query 'RouteTable.RouteTableId' \
        --output text)
    
    # Adiciona rota para Internet Gateway
    aws ec2 create-route \
        --route-table-id $ROUTE_TABLE_ID \
        --destination-cidr-block 0.0.0.0/0 \
        --gateway-id $IGW_ID
    
    # Associa subnet à route table
    aws ec2 associate-route-table \
        --subnet-id $SUBNET_ID \
        --route-table-id $ROUTE_TABLE_ID
    
    echo -e "${GREEN}✅ Route Table configurada${NC}"
    
    # Habilita auto-assign de IP público
    aws ec2 modify-subnet-attribute \
        --subnet-id $SUBNET_ID \
        --map-public-ip-on-launch
    
    echo -e "${GREEN}✅ Auto-assign de IP público habilitado${NC}"
}

# Cria cluster EKS
create_eks_cluster() {
    echo -e "${YELLOW}☸️  Criando cluster EKS...${NC}"
    
    eksctl create cluster \
        --name $CLUSTER_NAME \
        --region $REGION \
        --nodegroup-name rapidapi-nodes \
        --node-type t3.medium \
        --nodes 3 \
        --nodes-min 2 \
        --nodes-max 5 \
        --managed \
        --vpc-public-subnets $SUBNET_ID \
        --ssh-access \
        --ssh-public-key rapidapi-key \
        --full-ecr-access \
        --with-oidc \
        --install-storageclass
    
    echo -e "${GREEN}✅ Cluster EKS criado: $CLUSTER_NAME${NC}"
}

# Cria banco RDS
create_rds() {
    echo -e "${YELLOW}🗄️  Criando banco RDS...${NC}"
    
    # Cria subnet group para RDS
    aws rds create-db-subnet-group \
        --db-subnet-group-name rapidapi-subnet-group \
        --db-subnet-group-description "Subnet group para RapidAPI" \
        --subnet-ids $SUBNET_ID
    
    # Cria instância RDS
    aws rds create-db-instance \
        --db-instance-identifier rapidapi-postgres \
        --db-instance-class db.t3.micro \
        --engine postgres \
        --master-username rapidapi \
        --master-user-password rapidapi123 \
        --allocated-storage 20 \
        --db-subnet-group-name rapidapi-subnet-group \
        --vpc-security-group-ids $SECURITY_GROUP_ID \
        --backup-retention-period 7 \
        --preferred-backup-window 03:00-04:00 \
        --preferred-maintenance-window sun:04:00-sun:05:00 \
        --tags Key=Name,Value=rapidapi-postgres
    
    echo -e "${GREEN}✅ Instância RDS criada${NC}"
}

# Cria ElastiCache Redis
create_redis() {
    echo -e "${YELLOW}🔴 Criando ElastiCache Redis...${NC}"
    
    # Cria subnet group para ElastiCache
    aws elasticache create-subnet-group \
        --cache-subnet-group-name rapidapi-redis-subnet-group \
        --cache-subnet-group-description "Subnet group para Redis" \
        --subnet-ids $SUBNET_ID
    
    # Cria cluster Redis
    aws elasticache create-cache-cluster \
        --cache-cluster-id rapidapi-redis \
        --engine redis \
        --cache-node-type cache.t3.micro \
        --num-cache-nodes 1 \
        --cache-subnet-group-name rapidapi-redis-subnet-group \
        --security-group-ids $SECURITY_GROUP_ID \
        --tags Key=Name,Value=rapidapi-redis
    
    echo -e "${GREEN}✅ Cluster Redis criado${NC}"
}

# Configura CloudWatch
setup_cloudwatch() {
    echo -e "${YELLOW}📊 Configurando CloudWatch...${NC}"
    
    # Cria log group
    aws logs create-log-group --log-group-name /aws/eks/$CLUSTER_NAME/rapidapi
    
    # Cria dashboard
    aws cloudwatch put-dashboard \
        --dashboard-name RapidAPI-Production \
        --dashboard-body file://cloudwatch-dashboard.json
    
    echo -e "${GREEN}✅ CloudWatch configurado${NC}"
}

# Deploy da aplicação
deploy_application() {
    echo -e "${YELLOW}🚀 Deployando aplicação...${NC}"
    
    # Atualiza kubeconfig
    aws eks update-kubeconfig --name $CLUSTER_NAME --region $REGION
    
    # Cria namespace
    kubectl create namespace rapidapi-production
    kubectl create namespace rapidapi-monitoring
    
    # Aplica manifests
    kubectl apply -f k8s/namespace.yaml
    kubectl apply -f k8s/configmap.yaml
    kubectl apply -f k8s/secrets.yaml
    kubectl apply -f k8s/deployment.yaml
    
    # Deploy Prometheus Operator
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo update
    
    helm install prometheus prometheus-community/kube-prometheus-stack \
        --namespace rapidapi-monitoring \
        --create-namespace \
        --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false
    
    # Deploy Grafana
    helm repo add grafana https://grafana.github.io/helm-charts
    helm install grafana grafana/grafana \
        --namespace rapidapi-monitoring \
        --set adminPassword=admin123 \
        --set service.type=LoadBalancer
    
    echo -e "${GREEN}✅ Aplicação deployada com sucesso${NC}"
}

# Configura Load Balancer
setup_load_balancer() {
    echo -e "${YELLOW}⚖️  Configurando Load Balancer...${NC}"
    
    # Cria Application Load Balancer
    aws elbv2 create-load-balancer \
        --name rapidapi-alb \
        --subnets $SUBNET_ID \
        --security-groups $SECURITY_GROUP_ID \
        --scheme internet-facing \
        --type application
    
    echo -e "${GREEN}✅ Load Balancer configurado${NC}"
}

# Configura Auto Scaling
setup_autoscaling() {
    echo -e "${YELLOW}📈 Configurando Auto Scaling...${NC}"
    
    # Cria target tracking scaling policy
    kubectl autoscale deployment rapidapi-main \
        --cpu-percent=70 \
        --min=3 \
        --max=10 \
        --namespace rapidapi-production
    
    echo -e "${GREEN}✅ Auto Scaling configurado${NC}"
}

# Função principal
main() {
    echo -e "${BLUE}🚀 Iniciando deploy completo para AWS...${NC}"
    
    check_dependencies
    setup_aws
    create_network
    create_eks_cluster
    create_rds
    create_redis
    setup_cloudwatch
    deploy_application
    setup_load_balancer
    setup_autoscaling
    
    echo -e "${GREEN}🎉 Deploy AWS concluído com sucesso!${NC}"
    echo ""
    echo -e "${BLUE}📋 Informações do Deploy:${NC}"
    echo "  • Cluster EKS: $CLUSTER_NAME"
    echo "  • Região: $REGION"
    echo "  • VPC: $VPC_ID"
    echo "  • Subnet: $SUBNET_ID"
    echo ""
    echo -e "${BLUE}🌐 URLs de Acesso:${NC}"
    echo "  • Dashboard: http://localhost:8080"
    echo "  • Grafana: http://localhost:3000"
    echo "  • Prometheus: http://localhost:9090"
    echo ""
    echo -e "${YELLOW}⚠️  Lembre-se de:${NC}"
    echo "  • Configurar variáveis de ambiente"
    echo "  • Atualizar secrets com valores reais"
    echo "  • Configurar domínio e SSL"
    echo "  • Monitorar logs e métricas"
}

# Executa função principal
main "$@"
