"""
GITHUB INTEGRATION - Integración con GitHub
Gestiona repos, PRs, issues y más
"""

import logging
from typing import Dict, List, Optional
from github import Github, GithubException

logger = logging.getLogger(__name__)


class GitHubIntegration:
    """Integración con GitHub"""
    
    def __init__(self, token: str):
        self.token = token
        self.gh = None
        self.user = None
        self.connect()
    
    def connect(self):
        """Conectar con GitHub"""
        try:
            self.gh = Github(self.token)
            self.user = self.gh.get_user()
            logger.info(f"✅ GitHub conectado: {self.user.login}")
        except GithubException as e:
            logger.error(f"❌ Error conectando a GitHub: {e}")
    
    def get_repositories(self) -> List[Dict]:
        """Obtener lista de repositorios"""
        try:
            repos = []
            for repo in self.user.get_repos():
                repos.append({
                    'name': repo.name,
                    'url': repo.html_url,
                    'description': repo.description,
                    'stars': repo.stargazers_count,
                    'language': repo.language,
                    'updated_at': repo.updated_at.isoformat()
                })
            logger.info(f"✅ {len(repos)} repositorios obtenidos")
            return repos
        except Exception as e:
            logger.error(f"❌ Error obteniendo repos: {e}")
            return []
    
    def get_pull_requests(self, repo_name: str, state: str = 'open') -> List[Dict]:
        """Obtener PRs de un repositorio"""
        try:
            repo = self.user.get_repo(repo_name)
            prs = []
            
            for pr in repo.get_pulls(state=state):
                prs.append({
                    'number': pr.number,
                    'title': pr.title,
                    'author': pr.user.login,
                    'state': pr.state,
                    'url': pr.html_url,
                    'created_at': pr.created_at.isoformat(),
                    'updated_at': pr.updated_at.isoformat()
                })
            
            logger.info(f"✅ {len(prs)} PRs obtenidos de {repo_name}")
            return prs
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo PRs: {e}")
            return []
    
    def get_issues(self, repo_name: str, state: str = 'open') -> List[Dict]:
        """Obtener issues de un repositorio"""
        try:
            repo = self.user.get_repo(repo_name)
            issues = []
            
            for issue in repo.get_issues(state=state):
                issues.append({
                    'number': issue.number,
                    'title': issue.title,
                    'author': issue.user.login,
                    'state': issue.state,
                    'url': issue.html_url,
                    'labels': [label.name for label in issue.labels],
                    'created_at': issue.created_at.isoformat()
                })
            
            logger.info(f"✅ {len(issues)} issues obtenidos de {repo_name}")
            return issues
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo issues: {e}")
            return []
    
    def create_issue(self, repo_name: str, title: str, body: str) -> Optional[Dict]:
        """Crear nuevo issue"""
        try:
            repo = self.user.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body)
            
            logger.info(f"✅ Issue creado: {issue.number}")
            return {
                'number': issue.number,
                'title': issue.title,
                'url': issue.html_url
            }
        
        except Exception as e:
            logger.error(f"❌ Error creando issue: {e}")
            return None
    
    def create_pull_request(self, repo_name: str, title: str, head: str, base: str = 'main') -> Optional[Dict]:
        """Crear nuevo PR"""
        try:
            repo = self.user.get_repo(repo_name)
            pr = repo.create_pull(title=title, head=head, base=base)
            
            logger.info(f"✅ PR creado: {pr.number}")
            return {
                'number': pr.number,
                'title': pr.title,
                'url': pr.html_url
            }
        
        except Exception as e:
            logger.error(f"❌ Error creando PR: {e}")
            return None
    
    def get_commits(self, repo_name: str, branch: str = 'main', limit: int = 10) -> List[Dict]:
        """Obtener commits recientes"""
        try:
            repo = self.user.get_repo(repo_name)
            commits = []
            
            for commit in repo.get_commits(sha=branch)[:limit]:
                commits.append({
                    'sha': commit.sha[:7],
                    'message': commit.commit.message.split('\n')[0],
                    'author': commit.commit.author.name,
                    'date': commit.commit.author.date.isoformat(),
                    'url': commit.html_url
                })
            
            logger.info(f"✅ {len(commits)} commits obtenidos")
            return commits
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo commits: {e}")
            return []
    
    def get_repo_stats(self, repo_name: str) -> Dict:
        """Obtener estadísticas del repositorio"""
        try:
            repo = self.user.get_repo(repo_name)
            
            stats = {
                'name': repo.name,
                'description': repo.description,
                'url': repo.html_url,
                'stars': repo.stargazers_count,
                'forks': repo.forks_count,
                'watchers': repo.watchers_count,
                'open_issues': repo.open_issues_count,
                'language': repo.language,
                'created_at': repo.created_at.isoformat(),
                'updated_at': repo.updated_at.isoformat(),
                'size': repo.size,
                'topics': repo.topics
            }
            
            logger.info(f"✅ Estadísticas obtenidas para {repo_name}")
            return stats
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo estadísticas: {e}")
            return {}
    
    def watch_repository(self, repo_name: str) -> bool:
        """Seguir repositorio"""
        try:
            repo = self.user.get_repo(repo_name)
            repo.set_subscription(subscribed=True)
            logger.info(f"✅ Siguiendo repositorio: {repo_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error siguiendo repo: {e}")
            return False
    
    def star_repository(self, repo_name: str) -> bool:
        """Dar star a repositorio"""
        try:
            repo = self.user.get_repo(repo_name)
            self.user.add_to_starred(repo)
            logger.info(f"✅ Star agregado a: {repo_name}")
            return True
        except Exception as e:
            logger.error(f"❌ Error agregando star: {e}")
            return False
    
    def get_notifications(self) -> List[Dict]:
        """Obtener notificaciones"""
        try:
            notifications = []
            
            for notif in self.user.get_user().get_notifications():
                notifications.append({
                    'subject': notif.subject.get('title'),
                    'type': notif.subject.get('type'),
                    'repository': notif.repository.name,
                    'reason': notif.reason,
                    'unread': notif.unread,
                    'updated_at': notif.updated_at.isoformat()
                })
            
            logger.info(f"✅ {len(notifications)} notificaciones obtenidas")
            return notifications
        
        except Exception as e:
            logger.error(f"❌ Error obteniendo notificaciones: {e}")
            return []
    
    def search_repositories(self, query: str, language: Optional[str] = None) -> List[Dict]:
        """Buscar repositorios"""
        try:
            search_query = query
            if language:
                search_query += f" language:{language}"
            
            repos = []
            for repo in self.gh.search_repositories(search_query)[:10]:
                repos.append({
                    'name': repo.full_name,
                    'url': repo.html_url,
                    'description': repo.description,
                    'stars': repo.stargazers_count,
                    'language': repo.language
                })
            
            logger.info(f"✅ {len(repos)} repositorios encontrados")
            return repos
        
        except Exception as e:
            logger.error(f"❌ Error buscando repos: {e}")
            return []
