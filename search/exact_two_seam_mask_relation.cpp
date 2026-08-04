#include <bits/stdc++.h>
using namespace std;
struct Solver{
 int n,m; vector<pair<int,int>> E; vector<vector<pair<int,int>>> adj; vector<char> mat,sel,forbid; vector<int> deg,wit; long long calls,budget,prunes;
 bool add(int id,vector<int>&ch){if(sel[id])return true;sel[id]=1;ch.push_back(id);auto[a,b]=E[id];return ++deg[a]<=2&&++deg[b]<=2;}
 void undo(vector<int>&ch){for(int i=(int)ch.size()-1;i>=0;i--){int id=ch[i];sel[id]=0;auto[a,b]=E[id];--deg[a];--deg[b];}}
 bool closed(){vector<vector<int>> A(n);vector<char> vis(n);for(int i=0;i<m;i++)if(sel[i]){auto[a,b]=E[i];A[a].push_back(b);A[b].push_back(a);}for(int s=0;s<n;s++)if(!vis[s]&&!A[s].empty()){vector<int> c;stack<int>q;q.push(s);vis[s]=1;while(!q.empty()){int u=q.top();q.pop();c.push_back(u);for(int v:A[u])if(!vis[v])vis[v]=1,q.push(v);}if((int)c.size()<n){bool z=1;for(int v:c)if(deg[v]!=2)z=0;if(z){prunes++;return true;}}}return false;}
 int rec(int mc){if(++calls>budget)return -1;if(mc==n){if(accumulate(sel.begin(),sel.end(),0)!=n)return 0;vector<char>vis(n);stack<int>q;q.push(0);vis[0]=1;while(!q.empty()){int u=q.top();q.pop();for(auto[v,id]:adj[u])if(sel[id]&&!vis[v])vis[v]=1,q.push(v);}if(count(vis.begin(),vis.end(),1)==n){wit.clear();for(int i=0;i<m;i++)if(sel[i])wit.push_back(i);return 1;}return 0;}int u=-1,best=99;for(int x=0;x<n;x++)if(!mat[x]){int c=0;for(auto[v,id]:adj[x])if(!mat[v]&&!forbid[id])c++;if(!c)return 0;if(c<best)best=c,u=x;}for(auto[v,mid]:adj[u])if(!mat[v]&&!forbid[mid]){mat[u]=mat[v]=1;vector<int>ch;bool ok=1;for(auto[w,id]:adj[u])if(id!=mid&&!add(id,ch)){ok=0;break;}if(ok)for(auto[w,id]:adj[v])if(id!=mid&&!add(id,ch)){ok=0;break;}int z=0;if(ok&&!closed())z=rec(mc+2);undo(ch);mat[u]=mat[v]=0;if(z)return z;}return 0;}
 int solve(const vector<pair<int,int>>& constraints){mat.assign(n,0);sel.assign(m,0);forbid.assign(m,0);deg.assign(n,0);calls=prunes=0;wit.clear();vector<int>ch;int mc=0;vector<int> state(m,-1);
  for(auto[id,selected]:constraints){if(state[id]!=-1 && state[id]!=selected)return 0;state[id]=selected;}
  for(int id=0;id<m;id++)if(state[id]==1)forbid[id]=1;
  for(int id=0;id<m;id++)if(state[id]==0){auto[a,b]=E[id];if(mat[a]||mat[b])return 0;mat[a]=mat[b]=1;mc+=2;for(auto[w,e]:adj[a])if(e!=id&&!add(e,ch))return 0;for(auto[w,e]:adj[b])if(e!=id&&!add(e,ch))return 0;}
  if(closed())return 0;return rec(mc);
 }
};
int main(){ios::sync_with_stdio(false);cin.tie(nullptr);Solver s;cin>>s.n>>s.m;s.E.resize(s.m);s.adj.assign(s.n,{});for(int i=0;i<s.m;i++){int a,b;cin>>a>>b;s.E[i]={a,b};s.adj[a].push_back({b,i});s.adj[b].push_back({a,i});}vector<int>a(12);for(int&i:a)cin>>i;int B;cin>>B;vector<int>b(B);for(int&i:b)cin>>i;int K;cin>>K;vector<int> masks(K);for(int&i:masks)cin>>i;s.budget=100000000;
 for(int ma:masks)for(int mb=0;mb<(1<<B);mb++){vector<pair<int,int>> c;for(int i=0;i<12;i++)c.push_back({a[i],((ma>>i)&1)^((ma>>((i+1)%12))&1)});for(int i=0;i<B;i++)c.push_back({b[i],((mb>>i)&1)^((mb>>((i+1)%B))&1)});int z=s.solve(c);cout<<ma<<" "<<mb<<" "<<(z==1?"positive":z==0?"negative":"unknown")<<" "<<s.calls<<" "<<s.prunes<<" "<<s.wit.size();for(int e:s.wit)cout<<" "<<e;cout<<"\n";}
}
