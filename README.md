# Java Code Fixer

An AI-powered Java code execution and fixing tool with a Streamlit web interface. This application allows you to run Java code with different JDK versions and automatically fix compilation/runtime errors using Large Language Models.

## Features

- 🚀 **Multi-JDK Support**: Run Java code with JDK 8, 11, 17, and 21
- 🤖 **AI-Powered Code Fixing**: Automatically fix Java compilation and runtime errors using Anthropic Claude
- 🌐 **Web Interface**: User-friendly Streamlit interface
- 🐳 **Containerized**: Single Docker container with all JDK versions
- ☁️ **Cloud Ready**: Deploy on AWS ECS or locally

## Architecture

### Core Components

#### 1. `streamlit_ui.py` - Web Interface
- **Purpose**: Main Streamlit application providing the web interface
- **Features**:
  - Java code input text area
  - Java version selection dropdown (8, 11, 17, 21)
  - LLM model selection (Anthropic/OpenAI)
  - Code execution output display
  - AI-generated corrected code display
  - Run, Reset, and Generate Updated Code buttons
- **Configuration**: Uses `.streamlit/config.toml` for deployment compatibility

#### 2. `runner.py` - Java Execution Engine
- **Purpose**: Handles Java code compilation and execution
- **Key Functions**:
  - `extract_class_name()`: Extracts Java class name from code using regex
  - `run_java()`: Compiles and executes Java code with specified JDK version
- **Process**:
  1. Creates unique temporary directory
  2. Writes Java code to file with correct class name
  3. Compiles using specified JDK's javac
  4. Executes using specified JDK's java
  5. Returns execution results (success/failure, stdout, stderr)

#### 3. `java_code_fixer.py` - AI Code Fixing
- **Purpose**: Integrates with Anthropic Claude API to fix Java code issues
- **Key Functions**:
  - `fix_code()`: Sends Java code, error messages, and version to LLM for fixing
- **Features**:
  - Removes markdown formatting from LLM responses
  - Handles compilation and runtime errors
  - Returns clean, executable Java code

#### 4. `test_llm.py` - Testing Utility
- **Purpose**: Test the JavaCodeFixer functionality
- **Usage**: Validates API integration and code fixing capabilities

## Prerequisites

- Docker installed on your system
- AWS CLI configured (for ECS deployment)
- Anthropic API key (set as environment variable)

## Environment Variables

Create a `.env` file in the project root:

```env
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

## Local Development

### 1. Clone Repository
```bash
git clone https://github.com/RAKIBJAWED/java-code-fixer.git
cd java-code-fixer
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Locally
```bash
streamlit run streamlit_ui.py
```

Access at: `http://localhost:8501`

## Docker Deployment

### 1. Build Docker Image
```bash
docker build -t java-code-fixer .
```

### 2. Run Container Locally
```bash
docker run -d -p 8501:8501 --name java-code-fixer \
  -e ANTHROPIC_API_KEY=your_api_key_here \
  java-code-fixer
```

Access at: `http://localhost:8501`

### 3. Stop Container
```bash
docker stop java-code-fixer
docker rm java-code-fixer
```

## AWS ECS Deployment

### Prerequisites
- AWS CLI configured with appropriate permissions
- Docker image pushed to Amazon ECR

### Step 1: Create ECR Repository
```bash
aws ecr create-repository --repository-name java-code-fixer --region us-east-1
```

### Step 2: Build and Push Image
```bash
# Get ECR login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Tag and push image
docker tag java-code-fixer:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/java-code-fixer:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/java-code-fixer:latest
```

### Step 3: Create ECS Cluster
```bash
aws ecs create-cluster --cluster-name java-code-fixer-cluster --region us-east-1
```

### Step 4: Create IAM Role for ECS Tasks
```bash
# Create execution role
aws iam create-role --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policy
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

### Step 5: Register Task Definition
```bash
aws ecs register-task-definition \
  --family java-code-fixer-task \
  --network-mode awsvpc \
  --requires-compatibilities FARGATE \
  --cpu 1024 \
  --memory 2048 \
  --execution-role-arn arn:aws:iam::<account-id>:role/ecsTaskExecutionRole \
  --container-definitions '[{
    "name": "java-code-fixer",
    "image": "<account-id>.dkr.ecr.us-east-1.amazonaws.com/java-code-fixer:latest",
    "cpu": 1024,
    "memory": 2048,
    "essential": true,
    "portMappings": [{
      "containerPort": 8501,
      "protocol": "tcp"
    }],
    "environment": [{
      "name": "ANTHROPIC_API_KEY",
      "value": "your_api_key_here"
    }]
  }]'
```

### Step 6: Create Security Group
```bash
# Get default VPC ID
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)

# Create security group
aws ec2 create-security-group \
  --group-name java-code-fixer-sg \
  --description "Security group for Java Code Fixer" \
  --vpc-id $VPC_ID

# Allow inbound traffic on port 8501
aws ec2 authorize-security-group-ingress \
  --group-id <security-group-id> \
  --protocol tcp \
  --port 8501 \
  --cidr 0.0.0.0/0
```

### Step 7: Create ECS Service
```bash
# Get subnet IDs
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" "Name=default-for-az,Values=true" --query "Subnets[0:2].SubnetId" --output text)

# Create service
aws ecs create-service \
  --cluster java-code-fixer-cluster \
  --service-name java-code-fixer-service \
  --task-definition java-code-fixer-task:1 \
  --desired-count 1 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={
    subnets=[$SUBNET_IDS],
    securityGroups=[<security-group-id>],
    assignPublicIp=ENABLED
  }"
```

### Step 8: Get Public IP
```bash
# List tasks
aws ecs list-tasks --cluster java-code-fixer-cluster --service-name java-code-fixer-service

# Describe task to get ENI ID
aws ecs describe-tasks --cluster java-code-fixer-cluster --tasks <task-arn>

# Get public IP from ENI
aws ec2 describe-network-interfaces --network-interface-ids <eni-id> --query "NetworkInterfaces[0].Association.PublicIp"
```

Access your application at: `http://<public-ip>:8501`

## Usage

1. **Enter Java Code**: Paste or type your Java code in the input area
2. **Select Java Version**: Choose from JDK 8, 11, 17, or 21
3. **Run Code**: Click "Run Java Code" to execute
4. **Fix Errors**: If compilation/runtime errors occur, click "Generate Updated Code" to get AI-fixed version
5. **Reset**: Clear all inputs and outputs

## File Structure

```
java-code-fixer/
├── streamlit_ui.py          # Main Streamlit application
├── runner.py                # Java execution engine
├── java_code_fixer.py       # AI code fixing integration
├── test_llm.py              # Testing utility
├── requirements.txt         # Python dependencies
├── Dockerfile               # Container configuration
├── .streamlit/
│   └── config.toml          # Streamlit configuration
├── .env                     # Environment variables (create this)
└── README.md                # This file
```

## Dependencies

- **streamlit**: Web interface framework
- **anthropic**: Anthropic Claude API client
- **python-dotenv**: Environment variable management
- **docker**: Container runtime (for local execution)

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `ANTHROPIC_API_KEY` is set correctly
2. **Docker Issues**: Verify Docker is running and accessible
3. **Port Conflicts**: Change port mapping if 8501 is in use
4. **Memory Issues**: Increase container memory for large Java applications

### ECS Specific Issues

1. **Task Not Starting**: Check CloudWatch logs for container errors
2. **Network Issues**: Verify security group allows inbound traffic on port 8501
3. **Image Pull Errors**: Ensure ECR permissions are correctly configured

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally and with Docker
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review AWS ECS and Docker documentation for deployment issues
