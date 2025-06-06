To **set up ArgoCD in your Kubernetes cluster**, you can do it in **three main ways**:

---

## 🔧 OPTION 1: Install ArgoCD Using `kubectl` (Manual but Simple)

This is the **quickest** way to get ArgoCD running.

### ✅ Step-by-Step:

```bash
# 1. Create namespace
kubectl create namespace argocd

# 2. Install ArgoCD core components
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

> This installs the ArgoCD server, repo server, application controller, and UI.

---

### ✅ Access the ArgoCD UI:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open [https://localhost:8080](https://localhost:8080) in your browser.

---

### ✅ Get the initial admin password:

```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

Login with:

* **Username**: `admin`
* **Password**: (from above)

---

## 🚀 OPTION 2: Install ArgoCD via Helm (Best for Automation / Terraform)

This is ideal if you want to integrate ArgoCD install into **Terraform** or **CI/CD**.

### 1. Add Helm repo and update

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```

### 2. Install with Helm

```bash
helm upgrade --install argocd argo/argo-cd \
  --namespace argocd \
  --create-namespace \
  --version 6.7.4 # <-- Use latest stable
```

You can pass your `values.yaml` if you want to customize things (e.g., external ingress, resource limits).

---

## 🌐 (Optional) Expose ArgoCD via Ingress or LoadBalancer

For production, create an ingress or service:

### Option A: LoadBalancer (quick for testing)

```bash
kubectl patch svc argocd-server -n argocd -p '{"spec": {"type": "LoadBalancer"}}'
```

Then get the external IP:

```bash
kubectl get svc argocd-server -n argocd
```

### Option B: Ingress (for custom domain + HTTPS)

If you're using NGINX ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: argocd-ingress
  namespace: argocd
  annotations:
    nginx.ingress.kubernetes.io/backend-protocol: "HTTPS"
spec:
  rules:
    - host: argocd.yourdomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: argocd-server
                port:
                  number: 443
```

---

## ✅ After Installation: Bootstrap Your App

Create a file like `root-app.yaml` that points to your Git repo and path.

Then:

```bash
kubectl apply -f root-app.yaml -n argocd
```

ArgoCD will start syncing all your manifests or Helm charts from Git.

---

## 🧩 Summary

| Method     | Best For                     | Command                                     |
| ---------- | ---------------------------- | ------------------------------------------- |
| `kubectl`  | Quick install for dev/test   | `kubectl apply -f https://.../install.yaml` |
| `helm`     | CI/CD, Terraform, automation | `helm upgrade --install argo/argo-cd ...`   |
| Ingress/LB | Access via browser / domain  | Use Ingress or patch `svc` to LoadBalancer  |
