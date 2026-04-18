# 📜 Comment Marche Mon Site : [Colors](https://beijingg.vercel.app/colors/teste)
---
![](https://beijingg.vercel.app/colors/preview/preview.png/)

---
# ✨ 2 Méthodes pour l'utiliser (voir #🎨・colors )
# 🎫 1. URL
## Cette méthode est très rapide, collez votre URL et votre prénom, comme ceci :
## `beijingg.vercel.app/colors/` `prénom`
> ### page `beijingg.vercel.app/colors/prénom` ouverte
# 🖥 2. Interface
## Cette méthode est très facile, ouvrez le site :
## `beijingg.vercel.app/colors/`
## Entrez votre prénom, appuyez sur la flèche et c'est tout !
> ### page `beijingg.vercel.app/colors/prénom` ouverte

---

# 🧮 Comment ça marche ?
# Le site est hébergé avec [Vercel](vercel.com) (hébergeur de site gratuit), il y a deux fichiers :
## `index.html` - contient html, js, css
## `vercel.json`

---

# 🔎 Logique du site.
## Le `Json` détecte si, dans l'URL `beijingg.vercel.app/colors/`, il y a quelque chose après `colors/`, ensuite il envoie ce texte dans le html, le script s'occupe d'appliquer un calcul sur le texte.
## Il passe dans une fonction de hachage (djb2) qui le convertit en un nombre entier 32-bit. Ce nombre est ensuite lu en tranches via des opérations bit à bit pour extraire trois valeurs : une teinte (0°–360°), une saturation (55%–96%) et une luminosité (38%–68%) — soit une couleur complète en modèle HSL :
| Composante | Bits   | Plage       |
|------------|--------|-------------|
| Teinte     | 0 – 7  | 0° – 360°   |
| Saturation | 8 – 13 | 55% – 96%   |
| Luminosité | 14 – 18| 38% – 68%   |

---

# 🎓 Exemple
## Si on choisit leo, alors il passe par plusieurs étapes :
## `leo`
## → `djb2`
## → `3928471029`
## → `bits 0–7` : `teinte 214°`,
## → `bits 8–13` : `saturation 78%`,
## → `bits 14–18` : `luminosité 52%`
## → `hsl(214°, 78%, 52%)`
## `#2B6FD4`
## Donc si on entre `leo` alors on aura `#2B6FD4` comme couleur.

---

# 🎨 Texte css
## Une fois la couleur de fond définie, le site calcule sa luminance perçue pour choisir automatiquement entre texte noir et texte blanc — selon les standards d'accessibilité visuelle.

# Hébergement
## ✅ Grâce à cette technique :
HTML / CSS / JS vanilla — zéro dépendance
Hébergé sur Vercel (statique)
Aucune API, aucune base de données
