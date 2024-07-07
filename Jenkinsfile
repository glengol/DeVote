pipeline {
    agent {
        kubernetes {
            yamlFile 'build-pod.yaml'
            defaultContainer 'ez-docker-helm-build'
        }
    }
    environment {
        GITHUB_CREDENTIALS = credentials('git_hub')
        DOCKER_HUB_USERNAME = credentials('docker_hub')
        DOCKER_HUB_TOKEN = credentials('docker_hub')
        IMAGE_NAME = 'devote'
        TAG = 'latest'
    }
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        stage('Set up Docker Buildx') {
            steps {
                script {
                    sh 'docker run --rm --privileged multiarch/qemu-user-static --reset -p yes'
                    sh 'docker buildx create --use'
                }
            }
        }
        stage('Login to DockerHub') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker_hub', passwordVariable: 'DOCKER_HUB_CREDENTIALS_PSW', usernameVariable: 'DOCKER_HUB_CREDENTIALS_USR')]) {
                        // Use DOCKER_HUB_CREDENTIALS_USR and DOCKER_HUB_CREDENTIALS_PSW environment variables
                        docker.withRegistry('https://registry-1.docker.io/v2/', 'docker_hub') {
                            sh "echo \$DOCKER_HUB_CREDENTIALS_PSW | docker login -u \$DOCKER_HUB_CREDENTIALS_USR --password-stdin"
                        }
                    }
                }
            }
        }

        stage('Build and Run Containers') {
            steps {
                sh 'docker-compose up -d --build'
            }
        }

        stage('Install Dependencies and Run Tests') {
            steps {
                script {
                    // Install pytest in the python-test container
                    sh 'kubectl exec -it jenkins-agent-pod -n jenkins -c python-test -- pip install -U pytest'
                    // Run pytest in the python-test container
                    sh 'kubectl exec -it jenkins-agent-pod -n jenkins -c python-test -- pytest'
                }
            }
        }
        
        stage('Bump Version and Push Tag') {
            when {
                branch 'main'
            }
            steps {
                script {
                    def gitTag = sh(script: 'git describe --tags', returnStdout: true).trim()
                    env.TAG = gitTag

                    sh 'docker build -t ${IMAGE_NAME}:${TAG} .'
                    sh 'docker tag ${IMAGE_NAME}:${TAG} glengold/${IMAGE_NAME}:${TAG}'
                    sh 'docker push glengold/${IMAGE_NAME}:${TAG}'
                }
            }
        }
        stage('Clean up') {
            steps {
                sh 'docker-compose down'
            }
        }
    }
}
