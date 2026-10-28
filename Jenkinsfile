pipeline {
    agent any

    parameters {
        choice(name: 'APP_VERSION', choices: ['v1', 'v2', 'v3'], description: 'Select the application version to build and deploy')
    }

    environment {
        DOCKERHUB_REPO = 'docker7stage'
    }

    stages {
        stage('Build and Test') {
            steps {
                checkout scm
                script {
                    if (isUnix()) {
                        sh '''
                            python3 -m venv .venv
                            . .venv/bin/activate
                            pip install --upgrade pip
                            pip install -r requirements.txt
                            pytest -v
                        '''
                    } else {
                        bat '''
                            python -m venv .venv
                            call .venv\\Scripts\\activate.bat
                            python -m pip install --upgrade pip
                            python -m pip install -r requirements.txt
                            python -m pytest -v
                        '''
                    }
                }
            }
        }

        stage('Build and Push Docker Image') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                    script {
                        def imageTag = "${DOCKERHUB_USER}/${DOCKERHUB_REPO}:${params.APP_VERSION}"
                        if (isUnix()) {
                            sh """
                                docker build -t ${imageTag} .
                                echo "${DOCKERHUB_PASS}" | docker login -u "${DOCKERHUB_USER}" --password-stdin
                                docker push ${imageTag}
                                docker logout
                            """
                        } else {
                            powershell """
                                docker build -t ${imageTag} .
                                \$env:DOCKERHUB_PASS | docker login -u \$env:DOCKERHUB_USER --password-stdin
                                docker push ${imageTag}
                                docker logout
                            """
                        }
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub-credentials', usernameVariable: 'DOCKERHUB_USER', passwordVariable: 'DOCKERHUB_PASS')]) {
                    script {
                        def ver = params.APP_VERSION
                        def portMap = [v1: '30081', v2: '30082', v3: '30083']
                        def nodePort = portMap[ver]

                        if (isUnix()) {
                            sh """
                                sed 's|DOCKERHUB_USERNAME|${DOCKERHUB_USER}|g' k8s/deployment-${ver}.yaml | kubectl apply -f -
                                kubectl apply -f k8s/service-${ver}.yaml
                                kubectl rollout status deployment/docker7stage-${ver} --timeout=120s
                                kubectl get pods -l app=docker7stage-${ver}
                                kubectl get service docker7stage-${ver}
                                curl -f http://localhost:${nodePort}/health || true
                            """
                        } else {
                            powershell """
                                (Get-Content k8s/deployment-${ver}.yaml) -replace 'DOCKERHUB_USERNAME', '${DOCKERHUB_USER}' | kubectl apply -f -
                                kubectl apply -f k8s/service-${ver}.yaml
                                kubectl rollout status deployment/docker7stage-${ver} --timeout=120s
                                kubectl get pods -l app=docker7stage-${ver}
                                kubectl get service docker7stage-${ver}
                                try {
                                    \$res = Invoke-RestMethod -Uri "http://localhost:${nodePort}/health" -TimeoutSec 10
                                    Write-Output "Health Endpoint Response: \$(\$res | ConvertTo-Json -Compress)"
                                } catch {
                                    Write-Warning "Endpoint note: \$_"
                                }
                            """
                        }
                    }
                }
            }
        }
    }
}
