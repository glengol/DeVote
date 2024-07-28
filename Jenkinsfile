pipeline {
    agent {
        kubernetes {
            label 'jenkins-agent-pod'
            yamlFile 'build-pod.yaml'
        }
    }
    environment {
        DOCKER_CREDENTIALS_ID = 'docker_hub'
        DOCKER_IMAGE = 'glengold/images:python_pytest'
    }
    stages {
        stage('Checkout') {
            steps {
                git credentialsId: 'git_hub', url: 'https://github.com/glengol/DeVote.git'
            }
        }
        stage('Build Docker Image') {
            steps {
                container('ez-docker-helm-build') {
                    script {
                        docker.build(env.DOCKER_IMAGE)
                    }
                }
            }
        }
        stage('Run Tests') {
            steps {
                container('ez-docker-helm-build') {
                    script {
                        // Start the Flask application in the background
                        sh 'docker run -d -p 5000:5000 --name flask_app ${DOCKER_IMAGE} flask run --host=0.0.0.0'

                        // Give the Flask application a moment to start
                        sleep 10

                        // Run tests
                        sh 'docker exec flask_app pytest'
                    }
                }
            }
        }
        stage('Push Docker Image') {
            steps {
                container('ez-docker-helm-build') {
                    script {
                        docker.withRegistry('https://index.docker.io/v1/', env.DOCKER_CREDENTIALS_ID) {
                            docker.image(env.DOCKER_IMAGE).push()
                        }
                    }
                }
            }
        }
        stage('Clean Up') {
            steps {
                container('ez-docker-helm-build') {
                    script {
                        // Stop and remove the Flask container
                        sh 'docker stop flask_app && docker rm flask_app'

                        // Remove the Docker image
                        sh "docker rmi ${DOCKER_IMAGE}"
                    }
                }
            }
        }
    }
    post {
        always {
            cleanWs()
        }
    }
}
