

---

## 📖 Project Description

**DefNd** is a Python-based firewall that leverages `iptables` and `libnetfilter_queue` to intercept and filter network packets. Its philosophy is simple: *slow networks are secure networks*. By introducing controlled packet handling, DefNd provides a customizable way to enforce traffic rules, experiment with packet inspection, and enhance network security.

---
# DefNd 🔥
*A Python firewall: Because slow networks are much secure networks.*

---

## 🚀 Features
- Python-based firewall using `iptables` and `libnetfilter_queue`
- JSON-based configuration for flexible rule management
- Automatic cleanup of `iptables` rules on exit
- Example configuration included for quick setup

---

## 📦 Installation

This guide assumes installation on **Ubuntu 14.04 LTS**.  
DefNd may work on other Linux distributions, but compatibility is not guaranteed.

### Step 1: Install required packages
```bash
sudo apt-get install python python-pip iptables build-essential python-dev libnetfilter-queue-dev
```

### Step 2: Install Python dependencies
Dependencies are listed in `requirements.txt`. Install them with:
```bash
pip install --user -r requirements.txt
```

---

## ▶️ Running DefNd

The main entry point is `main.py`.  
Since DefNd modifies `iptables`, it must be run as **root**.

Example run with the provided configuration:
```bash
sudo python2 main.py examples/example.json
```

To stop DefNd, press **Control-C**.

---

## 🛠️ Troubleshooting

- **Internet not accessible after exit**  
  DefNd should undo its changes to `iptables`. If rules linger:
  ```bash
  sudo iptables -nL
  ```
  Look for rules with target chain `NFQUEUE`. Remove them with:
  ```bash
  sudo iptables -D INPUT -j NFQUEUE --queue-num 1
  sudo iptables -D OUTPUT -j NFQUEUE --queue-num 2
  ```

- **xtables lock error**  
  If another application holds the xtables lock:
  1. Stop DefNd with Control-C  
  2. Clear all lingering `iptables` rules  
  3. Restart DefNd  

---

## 📂 Project Structure
```
DefNd/
├── main.py                # Main firewall script
├── requirements.txt       # Python dependencies
├── examples/
│   └── example.json       # Sample configuration
└── README.md              # Documentation
```

---

## ⚠️ Notes
- Requires **Python 2.x** (tested with Python 2.7).
- Root privileges are mandatory for modifying `iptables`.
- Use with caution: improper rules may block all traffic.

---

## 📜 License
- Free to use, modify, and distribute.
```
