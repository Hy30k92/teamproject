pipeline {
    agent any

    environment {
        DOCKER_IMAGE_OWNER = 'hy30k'
        DOCKER_BUILD_TAG = "v${env.BUILD_NUMBER}"
        DOCKER_TOKEN = credentials('docker')
        GIT_CREDENTIALS = credentials('80645f1d-457f-473b-a0f4-f17a63e9e8e9')
        REPO_URL = 'hy30k92/teamproject.git'
        ARGOCD_REPO_URL = 'hy30k92/project-argo.git'
        COMMIT_MESSAGE = 'Update README.md via Jenkins Pipeline'
    }

    stages {
            stage('Clone from SCM') {
                steps {
                    dir('project-jenkins') {
                        git branch: 'master', url: "https://${GIT_CREDENTIALS_USR}:${GIT_CREDENTIALS_PSW}@github.com/${REPO_URL}"
                    }
                    dir('project-argocd') {
                        git branch: 'master', url: "https://${GIT_CREDENTIALS_USR}:${GIT_CREDENTIALS_PSW}@github.com/${ARGOCD_REPO_URL}"
                   }
            }
        }
    stage('Docker Image Building') {
          steps {
                sh '''
                docker build -t ${DOCKER_IMAGE_OWNER}/prj-frontend:latest ./frontend
                docker build -t ${DOCKER_IMAGE_OWNER}/prj-frontend:${DOCKER_BUILD_TAG} ./frontend
                docker build -t ${DOCKER_IMAGE_OWNER}/prj-admin:${DOCKER_BUILD_TAG} ./admin-service
                docker build -t ${DOCKER_IMAGE_OWNER}/prj-visitor:${DOCKER_BUILD_TAG} ./visitor-service
                '''
            }
        }

        stage('Docker Login') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'docker', usernameVariable: 'DOCKER_USR', passwordVariable: 'DOCKER_PWD')]) {
                    sh "echo $DOCKER_PWD | docker login -u $DOCKER_USR --password-stdin"
                }
            }
        }

        stage('Docker Image Pushing') {
            steps {
                sh '''
                docker push ${DOCKER_IMAGE_OWNER}/k8s-frontend:fpj
                docker push ${DOCKER_IMAGE_OWNER}/k8s-frontend:fpj${DOCKER_BUILD_TAG}
                docker push ${DOCKER_IMAGE_OWNER}/k8s-admin:fpj${DOCKER_BUILD_TAG}
                docker push ${DOCKER_IMAGE_OWNER}/k8s-visitor:fpj${DOCKER_BUILD_TAG}
                '''
            }
        }

        stage('Update ArgoCD values.yaml with Image Tags') {
            steps {
                dir('project-argo') {
                    sh """
                    sed -i "/${DOCKER_IMAGE_OWNER}\\/k8s-frontend:fpj/{n;s/tag: \\".*\\"/tag: \\"${DOCKER_BUILD_TAG}\\"/}" deploy-argocd/values.yaml
                    sed -i "/${DOCKER_IMAGE_OWNER}\\//k8s-admin:fpj/{n;s/tag: \\".*\\"/tag: \\"${DOCKER_BUILD_TAG}\\"/}" deploy-argocd/values.yaml
                    sed -i "/${DOCKER_IMAGE_OWNER}\\/k8s-visitor:fpj/{n;s/tag: \\".*\\"/tag: \\"${DOCKER_BUILD_TAG}\\"/}" deploy-argocd/values.yaml
                    """
                }
            }
        }

        stage('Commit Changes') {
            steps {
                dir('project-argo') {
                    script{
                        def changes = sh(script: "git status --porcelain", returnStdout: true).trim()
                        if (changes) {
                            sh '''
                            git config user.name "hy30k92"
                            git config user.email "hy30k92@jenkins.com"
                            git add deploy-argocd/values.yaml
                            git commit -m "Update image tags to ${DOCKER_BUILD_TAG}"
                            '''
                        } else {
                            echo "No changes to commit"
                        }
                    }
                }
            }
        }

        stage('Push Changes') {
            steps {
                dir('project-argo') {
                    withCredentials([usernamePassword(credentialsId: 'github_token', usernameVariable: 'GIT_CREDENTIALS_USR', passwordVariable: 'GIT_CREDENTIALS_PSW')]) {
                        sh '''
                        git push https://${GIT_CREDENTIALS_USR}:${GIT_CREDENTIALS_PSW}@github.com/${ARGOCD_REPO_URL} master
                        '''
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
