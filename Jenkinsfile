# Secured Jenkinsfile with DevSecOps pipeline
# This implements the "to-be" pipeline with comprehensive security controls

pipeline {
    agent any
    
    // Environment variables
    environment {
        DOCKER_IMAGE_NAME = "devsecops-flask"
        DOCKER_TAG = "${env.GIT_COMMIT.take(7)}"
        REPORTS_DIR = "reports"
    }
    
    // Build triggers - can be webhook or pollSCM
    triggers {
        pollSCM('H/5 * * * *')  // Poll every 5 minutes
    }
    
    stages {
        // Stage 1: Checkout source code
        stage('Checkout') {
            steps {
                checkout scm
                echo 'Code checked out successfully'
                sh 'git rev-parse HEAD > GIT_COMMIT'
                script {
                    env.GIT_COMMIT = readFile('GIT_COMMIT').trim()
                }
            }
        }
        
        // Stage 2: Install dependencies and run tests
        stage('Install and Test') {
            steps {
                echo 'Installing dependencies and running tests'
                sh '''
                    python -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install -r requirements-dev.txt
                    pytest --cov=app --cov-report=xml --cov-report=html --junitxml=pytest-report.xml
                '''
            }
            post {
                always {
                    junit 'pytest-report.xml'
                    publishHTML(target: [
                        reportDir: 'htmlcov',
                        reportFiles: 'index.html',
                        reportName: 'Coverage Report'
                    ])
                }
                failure {
                    error 'Tests failed - blocking pipeline'
                }
            }
        }
        
        // Stage 3: Secrets scanning with Gitleaks
        stage('Secrets Scan') {
            steps {
                echo 'Scanning for secrets with Gitleaks'
                sh '''
                    mkdir -p ${REPORTS_DIR}
                    docker run --rm -v ${WORKSPACE}:/src zricethezav/gitleaks:v8.18.0 detect --source /src --verbose --report-path /src/${REPORTS_DIR}/gitleaks-report.json --report-format json || true
                '''
                script {
                    def gitleaksOutput = readFile("${REPORTS_DIR}/gitleaks-report.json")
                    if (gitleaksOutput.contains('"findings":[') && !gitleaksOutput.contains('"findings":[]')) {
                        error 'Gitleaks found secrets - blocking pipeline'
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/gitleaks-report.json", fingerprint: true
                }
            }
        }
        
        // Stage 4: SAST with Semgrep, Bandit, and SonarQube
        stage('SAST') {
            parallel {
                stage('Semgrep') {
                    steps {
                        echo 'Running Semgrep SAST'
                        sh '''
                            mkdir -p ${REPORTS_DIR}
                            docker run --rm -v ${WORKSPACE}:/src returntocorp/semgrep:1.45.0 --config /src/.semgrep/custom.yaml --config auto --json --output /src/${REPORTS_DIR}/semgrep-report.json /src/app || true
                        '''
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: "${REPORTS_DIR}/semgrep-report.json", fingerprint: true
                        }
                    }
                }
                stage('Bandit') {
                    steps {
                        echo 'Running Bandit Python SAST'
                        sh '''
                            mkdir -p ${REPORTS_DIR}
                            docker run --rm -v ${WORKSPACE}:/src python:3.11-slim bash -c "cd /src && pip install bandit==1.7.5 && bandit -r app -f json -o /src/${REPORTS_DIR}/bandit-report.json" || true
                        '''
                    }
                    post {
                        always {
                            archiveArtifacts artifacts: "${REPORTS_DIR}/bandit-report.json", fingerprint: true
                        }
                    }
                }
                stage('SonarQube') {
                    steps {
                        echo 'Running SonarQube analysis'
                        withSonarQubeEnv('SonarQube') {
                            sh '''
                                . venv/bin/activate
                                sonar-scanner
                            '''
                        }
                    }
                }
            }
            post {
                failure {
                    error 'SAST found critical/high issues - blocking pipeline'
                }
            }
        }
        
        // Stage 5: SonarQube Quality Gate
        stage('SonarQube Quality Gate') {
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        waitForQualityGate abortPipeline: true
                    }
                }
            }
        }
        
        // Stage 6: Dependency scanning with Trivy
        stage('Scan Dependencies') {
            steps {
                echo 'Scanning dependencies with Trivy'
                sh '''
                    mkdir -p ${REPORTS_DIR}
                    docker run --rm -v ${WORKSPACE}:/src aquasec/trivy:0.47.0 fs --format json --output /src/${REPORTS_DIR}/trivy-fs-report.json --severity CRITICAL,HIGH,MEDIUM,LOW /src || true
                '''
                script {
                    // Parse Trivy output and fail on CRITICAL/HIGH
                    def trivyOutput = readFile("${REPORTS_DIR}/trivy-fs-report.json")
                    def trivyJson = readJSON text: trivyOutput
                    def criticalCount = trivyJson.Results.Results.sum { it.Vulnerabilities?.count { it.Severity == 'CRITICAL' } ?: 0 }
                    def highCount = trivyJson.Results.Results.sum { it.Vulnerabilities?.count { it.Severity == 'HIGH' } ?: 0 }
                    
                    if (criticalCount > 0 || highCount > 0) {
                        error "Trivy found ${criticalCount} CRITICAL and ${highCount} HIGH vulnerabilities - blocking pipeline"
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/trivy-fs-report.json", fingerprint: true
                }
            }
        }
        
        // Stage 7: IaC scanning with Checkov (non-blocking)
        stage('IaC Scan') {
            steps {
                echo 'Scanning Dockerfile with Checkov'
                catchError(buildResult: 'SUCCESS', stageResult: 'UNSTABLE') {
                    sh '''
                        mkdir -p ${REPORTS_DIR}
                        docker run --rm -v ${WORKSPACE}:/src bridgecrew/checkov:3.2.65 -f /src/Dockerfile -o json --output-file-path /src/${REPORTS_DIR}/checkov-report.json || true
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/checkov-report.json", fingerprint: true
                }
            }
        }
        
        // Stage 8: Build Docker image
        stage('Docker Build') {
            steps {
                echo 'Building Docker image'
                sh "docker build -t ${DOCKER_IMAGE_NAME}:${DOCKER_TAG} -t ${DOCKER_IMAGE_NAME}:latest ."
            }
            post {
                failure {
                    error 'Docker build failed - blocking pipeline'
                }
            }
        }
        
        // Stage 9: Docker image scanning with Trivy
        stage('Docker Scan') {
            steps {
                echo 'Scanning Docker image with Trivy'
                sh '''
                    mkdir -p ${REPORTS_DIR}
                    docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.47.0 image --format json --output ${REPORTS_DIR}/trivy-image-report.json --severity CRITICAL,HIGH,MEDIUM,LOW ${DOCKER_IMAGE_NAME}:${DOCKER_TAG} || true
                '''
                script {
                    // Parse Trivy output and fail on CRITICAL/HIGH
                    def trivyOutput = readFile("${REPORTS_DIR}/trivy-image-report.json")
                    def trivyJson = readJSON text: trivyOutput
                    def criticalCount = trivyJson.Results?.Vulnerabilities?.count { it.Severity == 'CRITICAL' } ?: 0
                    def highCount = trivyJson.Results?.Vulnerabilities?.count { it.Severity == 'HIGH' } ?: 0
                    
                    if (criticalCount > 0 || highCount > 0) {
                        error "Trivy image scan found ${criticalCount} CRITICAL and ${highCount} HIGH vulnerabilities - blocking pipeline"
                    }
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/trivy-image-report.json", fingerprint: true
                }
            }
        }
        
        // Stage 10: SBOM generation with Syft (non-blocking)
        stage('SBOM') {
            steps {
                echo 'Generating SBOM with Syft'
                catchError(buildResult: 'SUCCESS', stageResult: 'SUCCESS') {
                    sh '''
                        mkdir -p ${REPORTS_DIR}
                        docker run --rm -v /var/run/docker.sock:/var/run/docker.sock anchore/syft:0.103.0 ${DOCKER_IMAGE_NAME}:${DOCKER_TAG} -o cyclonedx-json > ${REPORTS_DIR}/sbom.json || true
                    '''
                }
            }
            post {
                always {
                    archiveArtifacts artifacts: "${REPORTS_DIR}/sbom.json", fingerprint: true
                }
            }
        }
        
        // Stage 11: Deploy to staging
        stage('Deploy Staging') {
            steps {
                echo 'Deploying to staging environment'
                sh '''
                    # Run container in staging network
                    docker network create devsecops-staging || true
                    docker run -d --name staging-${DOCKER_TAG} --network devsecops-staging -p 5001:5000 --env-file .env ${DOCKER_IMAGE_NAME}:${DOCKER_TAG}
                    # Wait for container to be ready
                    sleep 10
                '''
            }
            post {
                always {
                    sh 'docker logs staging-${DOCKER_TAG} || true'
                }
                failure {
                    sh 'docker rm -f staging-${DOCKER_TAG} || true'
                    error 'Staging deployment failed - blocking pipeline'
                }
            }
        }
        
        // Stage 12: DAST with OWASP ZAP
        stage('DAST') {
            steps {
                echo 'Running OWASP ZAP DAST scan'
                sh '''
                    mkdir -p ${REPORTS_DIR}
                    docker run --rm --network devsecops-staging -t zaproxy/zap-stable:2.15.0 zap-baseline.py -t http://staging-${DOCKER_TAG}:5000 -r ${REPORTS_DIR}/zap-report.html -J ${REPORTS_DIR}/zap-report.json || true
                '''
                script {
                    // Parse ZAP output for HIGH severity issues
                    def zapOutput = readFile("${REPORTS_DIR}/zap-report.json")
                    def zapJson = readJSON text: zapOutput
                    def highCount = zapJson.site?.find { it.'@alerts' }?.'@alerts'?.count { it.riskcode == '3' } ?: 0
                    
                    if (highCount > 0) {
                        error "ZAP found ${highCount} HIGH severity issues - blocking pipeline"
                    }
                }
            }
            post {
                always {
                    publishHTML(target: [
                        reportDir: "${REPORTS_DIR}",
                        reportFiles: 'zap-report.html',
                        reportName: 'ZAP DAST Report'
                    ])
                    archiveArtifacts artifacts: "${REPORTS_DIR}/zap-report.json", fingerprint: true
                    sh 'docker rm -f staging-${DOCKER_TAG} || true'
                }
            }
        }
        
        // Stage 13: Push to Docker Hub (only on main branch)
        stage('Docker Push') {
            when {
                branch 'main'
            }
            steps {
                echo 'Pushing image to Docker Hub'
                withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                    sh '''
                        echo $DOCKER_PASS | docker login -u $DOCKER_USER --password-stdin
                        docker push ${DOCKER_IMAGE_NAME}:${DOCKER_TAG}
                        docker push ${DOCKER_IMAGE_NAME}:latest
                        docker logout
                    '''
                }
            }
            post {
                failure {
                    error 'Docker push failed - blocking pipeline'
                }
            }
        }
        
        // Stage 14: Deploy to Vercel (only on main branch)
        stage('Deploy Vercel') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying to Vercel'
                withCredentials([string(credentialsId: 'vercel-token', variable: 'VERCEL_TOKEN'), 
                               string(credentialsId: 'vercel-org-id', variable: 'VERCEL_ORG_ID'),
                               string(credentialsId: 'vercel-project-id', variable: 'VERCEL_PROJECT_ID')]) {
                    sh '''
                        # Install Vercel CLI
                        npm install -g vercel
                        
                        # Deploy to production
                        vercel deploy --prod --yes --token $VERCEL_TOKEN
                        
                        # Smoke test
                        sleep 5
                        curl -f https://your-vercel-url.vercel.app/health || exit 1
                    '''
                }
            }
            post {
                failure {
                    error 'Vercel deployment failed - blocking pipeline'
                }
            }
        }
    }
    
    post {
        always {
            echo 'Pipeline completed - archiving reports'
            archiveArtifacts artifacts: "${REPORTS_DIR}/**/*", fingerprint: true
            cleanWs()
        }
        success {
            echo 'Pipeline succeeded - all security gates passed'
            // Add notification here (email, Slack, etc.)
        }
        failure {
            echo 'Pipeline failed - security gates not met'
            // Add notification here (email, Slack, etc.)
        }
        unstable {
            echo 'Pipeline unstable - non-blocking security issues found'
            // Add notification here (email, Slack, etc.)
        }
    }
}
