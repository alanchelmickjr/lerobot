# Conda Decision Guide for LeRobot

## Quick Decision Tree

```
Do you ONLY need LeRobot?
    → Use Miniconda (Recommended)

Do you ALSO do data science work (Jupyter, pandas, etc.)?
    → Use Anaconda

Already have Anaconda installed?
    → Keep it, just create the lerobot environment

Want the fastest, cleanest setup?
    → Use Miniconda
```

## Detailed Comparison

| Feature | Miniconda | Anaconda |
|---------|-----------|----------|
| **Size** | ~400MB | ~3GB |
| **Packages** | Only conda + Python | 250+ packages |
| **Installation Time** | ~2 minutes | ~10 minutes |
| **Best For** | LeRobot, robotics, lightweight | Data science, ML, research |
| **Update Speed** | Fast | Slower |
| **System Resources** | Minimal | Higher |

## For LeRobot Specifically

### ✅ Miniconda is BETTER because:
- LeRobot only needs: Python 3.10, ffmpeg, pip packages
- Faster conda operations
- Less chance of package conflicts
- Cleaner environment management
- Works on ALL systems (Mac, Linux, Pi, etc.)

### ⚠️ Anaconda works but:
- Includes 250+ packages you won't use
- Takes more disk space
- Slower environment creation
- More potential conflicts

## Can They Coexist?

**SHORT ANSWER: NO - Don't install both!**

### Why not?
- PATH conflicts (which conda runs?)
- Environment confusion
- Package resolution conflicts
- Duplicate Python installations

### What if I need both ecosystems?
Choose Anaconda and use it for both:
```bash
# Data science environment
conda create -n datascience numpy pandas jupyter scikit-learn

# LeRobot environment  
conda create -n lerobot python=3.10
conda activate lerobot
pip install -e ".[feetech]"
```

## Migration Scenarios

### Currently have Anaconda, want Miniconda:
1. Run cleanup_conda.sh to remove Anaconda
2. Install Miniconda
3. Recreate your environments

### Currently have Miniconda, need data science:
Option 1: Keep Miniconda, install packages as needed
```bash
conda install numpy pandas jupyter matplotlib
```

Option 2: Switch to Anaconda
1. Backup environment specs: `conda env export > environment.yml`
2. Run cleanup_conda.sh
3. Install Anaconda
4. Recreate: `conda env create -f environment.yml`

## Cleanup Script Coverage

The `cleanup_conda.sh` script removes ALL conda variants:

### From Homebrew:
- ✅ miniconda
- ✅ anaconda
- ✅ conda

### From Local Directories:
- ✅ ~/miniconda3
- ✅ ~/anaconda3
- ✅ ~/miniforge3
- ✅ /opt/miniconda3
- ✅ /opt/anaconda3

### Configuration Files:
- ✅ ~/.conda
- ✅ ~/.condarc
- ✅ ~/.config/conda

### Shell Configurations:
- ✅ Removes conda init from ~/.zshrc
- ✅ Removes conda init from ~/.bashrc
- ✅ Removes conda init from ~/.bash_profile

## Platform Notes

### Raspberry Pi / ARM Systems
- Miniconda: Full support, lightweight, perfect
- Anaconda: Limited ARM support, heavy for Pi

### macOS (M1/M2/M3)
- Both work well
- Miniconda recommended for robotics

### Linux Desktop/Server
- Both work well
- Choose based on use case

## Final Recommendation for LeRobot

**USE MINICONDA** unless you're already heavily invested in Anaconda for other work.

```bash
# The complete LeRobot setup with Miniconda:
# 1. Install Miniconda (see FRESH_INSTALL_GUIDE.md)
# 2. Create environment
conda create -n lerobot python=3.10
conda activate lerobot
conda install ffmpeg -c conda-forge
cd ~/dev/GitHub/lerobot
pip install -e ".[feetech]"
# 3. Run calibration
python -m lerobot.scripts.auto_calibrate_so101
```

## TL;DR

- **Miniconda** = Lightweight, perfect for LeRobot
- **Anaconda** = Heavy, for data science
- **Don't install both** = They conflict
- **Already have one?** = Keep it, don't switch unless needed
- **Cleanup script** = Removes ALL conda variants completely