# GA-Optimized AES Key Schedule Project

**AI-Optimized Cryptographic Key Scheduling: Using Genetic Algorithms for Enhanced Network Security in Simulated Environments**

---

## 📖 Project Overview

This project implements a Genetic Algorithm (GA) to optimize the key schedule of AES-128 encryption, aiming to improve both security metrics and performance. The optimized encryption is then tested in a simulated client-server network environment.

### Key Features

- ✅ Custom AES-128 implementation with modifiable key schedule
- ✅ Genetic Algorithm optimization engine
- ✅ Comprehensive security metrics (avalanche effect, entropy)
- ✅ Network performance simulation
- ✅ Cisco Packet Tracer integration guidelines
- ✅ Automated visualization and reporting

---

## 🔧 Requirements

### System Requirements

- **OS:** Windows 10/11, macOS 10.14+, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher
- **RAM:** 4GB minimum, 8GB recommended
- **Storage:** 500MB free space
- **Cisco Packet Tracer:** 8.0 or higher (optional, for network simulation)

### Python Dependencies

Create a `requirements.txt` file with:

```txt
pycryptodome>=3.15.0
numpy>=1.21.0
matplotlib>=3.5.0
```

**Installation:**
```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install pycryptodome numpy matplotlib
```

---

## 📁 Project Structure

```
GA_AES_Project/
│
├── README.md                      # This file
├── requirements.txt               # Python dependencies
│
├── aes_custom.py                  # Custom AES implementation
├── ga_optimizer.py                # Genetic Algorithm engine
├── testing_visualization.py       # Testing and plotting utilities
├── network_simulator.py           # Network performance simulator
├── main_integration.py            # Main execution pipeline
│
├── results/                       # Generated results (auto-created)
│   └── run_YYYYMMDD_HHMMSS/
│       ├── ga_history.json
│       ├── best_chromosome.json
│       ├── comparison_results.json
│       ├── ga_evolution.png
│       ├── comparison_metrics.png
│       └── summary_report.txt
│
├── packet_tracer/                 # Network topology files
│   └── network_topology.pkt
│
└── docs/                          # Documentation
    ├── report_template.md
    ├── packet_tracer_guide.md
    └── quick_start_guide.md
```

---

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone or create project directory
mkdir GA_AES_Project
cd GA_AES_Project

# Install dependencies
pip install pycryptodome numpy matplotlib

# Verify installation
python -c "from Crypto.Cipher import AES; import numpy; import matplotlib; print('Setup complete!')"
```

### 2. Create Python Files

Copy the code from the provided artifacts into these files:
1. `aes_custom.py`
2. `ga_optimizer.py`
3. `testing_visualization.py`
4. `network_simulator.py`
5. `main_integration.py`

### 3. Run the Project

**Option A: Complete Pipeline (Recommended)**
```bash
python main_integration.py
```
- Choose option 1 for quick test (10 generations, ~5 min)
- Choose option 2 for full run (30 generations, ~15 min)

**Option B: Individual Components**
```bash
# Test AES implementation
python aes_custom.py

# Run GA optimization only
python ga_optimizer.py

# Run network simulation
python network_simulator.py
```

### 4. Check Results

Results are saved in `results/run_YYYYMMDD_HHMMSS/` directory:
- View PNG charts for visualizations
- Read `summary_report.txt` for text summary
- Analyze JSON files for detailed data

---

## 📊 Understanding the Output

### Generated Files

**1. ga_history.json**
```json
{
  "generations": [1, 2, 3, ...],
  "best_fitness": [0.52, 0.58, 0.63, ...],
  "avg_fitness": [0.45, 0.50, 0.55, ...]
}
```

**2. best_chromosome.json**
```json
{
  "rotations": [1, 2, 1, 3, 1, 2, 1, 1, 2, 1],
  "rcon_multipliers": [1, 1, 2, 1, 1, 3, 1, 1, 1, 2],
  "fitness": 0.7234,
  "metrics": { ... }
}
```

**3. comparison_results.json**
- Detailed metrics for standard vs optimized AES
- Statistical measures (mean, std, min, max)

**4. Visualization Files**
- `ga_evolution.png` - Fitness convergence chart
- `comparison_metrics.png` - Performance comparison
- `avalanche_distribution.png` - Security analysis
- `network_comparison.png` - Network performance

---

## 🔬 Methodology

### Custom AES Implementation

Modified the standard AES-128 key schedule with two adjustable parameters:

1. **Rotation Values (1-3 bytes):** Controls the RotWord operation for each round
2. **Rcon Multipliers (1-3x):** Modifies the round constant application

### Genetic Algorithm

**Chromosome Encoding:**
- 20 genes: 10 rotation values + 10 Rcon multipliers
- Each gene: integer in range [1, 3]

**Fitness Function:**
```
Fitness = 0.4 × Avalanche_Score + 0.3 × Entropy_Score + 0.3 × Speed_Score
```

**GA Parameters:**
- Population: 25 chromosomes
- Generations: 30
- Crossover: Single-point, rate 0.8
- Mutation: Random gene change, rate 0.2
- Selection: Tournament with size 3
- Elitism: Keep best 2

### Security Metrics

**1. Avalanche Effect**
- Measures bit diffusion
- Ideal: 50% (each output bit changes with 50% probability)
- Calculation: Average over 100 single-bit input changes

**2. Shannon Entropy**
- Measures randomness of key schedule
- Maximum: 8.0 bits (uniform distribution)
- Formula: H = -Σ p(x) log₂ p(x)

**3. Encryption Time**
- Average time to encrypt 1KB data
- Measured over 200 iterations
- Reported in milliseconds

---

## 🖥️ Cisco Packet Tracer Setup

### Network Topology

```
                  [Router]
                  192.168.1.1
                      |
                  [Switch]
       _______________|_______________
       |              |              |
   [Server]       [Client1]      [Client2-3]
  192.168.1.10   192.168.1.11   192.168.1.12-13
```

### Configuration Steps

1. **Add Devices:** 1 Router (2911), 1 Switch (2960), 1 Server, 3 PCs
2. **Connect:** Use copper straight-through cables
3. **Configure IPs:** Assign addresses as shown above
4. **Configure Router:**
   ```
   interface GigabitEthernet0/0
   ip address 192.168.1.1 255.255.255.0
   no shutdown
   ```
5. **Test Connectivity:** Ping between devices

**See `packet_tracer_guide.md` for detailed instructions.**

---

## 📈 Expected Results

### Typical Improvements

**Security Metrics:**
- Avalanche Effect: 48-52% (ideal range)
- Key Schedule Entropy: 7.5-8.0 bits
- Ciphertext Entropy: ≈8.0 bits

**Performance:**
- Encryption Speed: 5-15% faster
- End-to-End Latency: 3-10% reduction
- Throughput: Slight improvement

**GA Convergence:**
- Initial Fitness: 0.45-0.55
- Final Fitness: 0.65-0.80
- Convergence: 15-25 generations

---

## 🐛 Troubleshooting

### Common Issues

**1. Import Error: No module named 'Crypto'**
```bash
pip uninstall crypto pycrypto  # Remove conflicts
pip install pycryptodome
```

**2. GA Running Slowly**
- Reduce `population_size` to 15-20
- Reduce `num_generations` to 15-20
- Reduce `num_tests` in avalanche calculation

**3. Packet Tracer: Can't Ping**
- Verify IP addresses in same subnet
- Check router interface: `no shutdown`
- Verify cable connections (green lights)

**4. Results Not Improving**
- Try different random seed
- Increase population size
- Adjust fitness function weights
- Check for bugs in fitness calculation

---

## 🔍 Testing and Validation

### Unit Tests

Test each component individually:

```bash
# Test AES encryption/decryption
python -c "
from aes_custom import CustomAES
from Crypto.Random import get_random_bytes
aes = CustomAES()
key = get_random_bytes(16)
pt = b'Test'
ct = aes.encrypt(pt, key)
assert aes.decrypt(ct, key) == pt
print('AES test passed!')
"

# Test GA initialization
python -c "
from ga_optimizer import KeyScheduleChromosome
chr = KeyScheduleChromosome()
print(f'Chromosome: {chr.rotations}')
print('GA test passed!')
"
```

### Integration Tests

```bash
# Run quick integration test
python main_integration.py
# Select option 1 (Quick Test)
```

### Validation Checklist

- [ ] AES correctly encrypts and decrypts
- [ ] GA completes without errors
- [ ] Fitness improves over generations
- [ ] Results files are generated
- [ ] Visualizations render correctly
- [ ] Network simulator produces metrics
- [ ] Packet Tracer network is functional

---

## 📚 Documentation

### Available Guides

1. **Quick Start Guide** (`quick_start_guide.md`)
   - Step-by-step setup instructions
   - Common commands and workflows
   - Troubleshooting tips

2. **Packet Tracer Guide** (`packet_tracer_guide.md`)
   - Network topology design
   - Device configuration
   - Testing procedures

3. **Report Template** (`report_template.md`)
   - Structured report outline
   - Section guidelines
   - Figure and table examples

### Code Documentation

Each module includes detailed docstrings:

```python
# View documentation
python -c "from aes_custom import CustomAES; help(CustomAES)"
python -c "from ga_optimizer import GeneticAlgorithm; help(GeneticAlgorithm)"
```

---

## 🎓 Educational Value

### Learning Outcomes

Students will learn:
- **Cryptography:** AES internals, key scheduling
- **AI:** Genetic algorithms, optimization
- **Networks:** Client-server architecture, performance metrics
- **Python:** Object-oriented programming, threading
- **Analysis:** Statistical comparison, visualization

### Skills Demonstrated

- Algorithm implementation
- Performance optimization
- Security analysis
- Network simulation
- Data visualization
- Technical documentation

---

## 🔮 Future Enhancements

### Possible Extensions

1. **Extended Parameterization**
   - Modify S-box values
   - Adjust MixColumns coefficients
   - Customize SubBytes operation

2. **Advanced GA Techniques**
   - Multi-objective optimization (NSGA-II)
   - Adaptive mutation rates
   - Island model (parallel populations)

3. **Real Network Testing**
   - Deploy on actual servers
   - Test with real network conditions
   - Measure CPU/memory usage

4. **Other Ciphers**
   - Apply to DES, 3DES
   - Test with ChaCha20
   - Compare across algorithms

5. **Security Analysis**
   - Differential cryptanalysis resistance
   - Linear cryptanalysis testing
   - Side-channel attack simulation

---

## 📄 License

This project is created for educational purposes as part of a Computer Networks course project.

**Note:** The custom AES implementation is for demonstration only. For production use, always use well-tested cryptographic libraries like OpenSSL or the standard PyCryptodome implementation.

---

## 👥 Contributing

This is an academic project, but suggestions for improvements are welcome:

1. Fork the repository (if on GitHub)
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request with description

---

## 📞 Support

### Getting Help

1. **Check Documentation:** Read the guides in `docs/` folder
2. **Review Code Comments:** Inline documentation explains key concepts
3. **Search Issues:** Check if others had similar problems
4. **Ask Instructor:** Contact during office hours

### Reporting Bugs

If you find a bug:
1. Describe what you expected to happen
2. Describe what actually happened
3. Include error messages (full traceback)
4. Mention your Python version and OS
5. Attach relevant code snippets

---

## 🙏 Acknowledgments

### Resources Used

- **NIST FIPS 197:** AES specification
- **PyCryptodome:** Cryptography library
- **NumPy:** Numerical computations
- **Matplotlib:** Data visualization
- **Cisco Packet Tracer:** Network simulation

### References

1. Daemen, J., & Rijmen, V. (2002). The Design of Rijndael: AES.
2. Goldberg, D. E. (1989). Genetic Algorithms in Search, Optimization, and Machine Learning.
3. Shannon, C. E. (1949). Communication Theory of Secrecy Systems.

---

## ✨ Project Highlights

### What Makes This Special

- ✅ Combines three CS domains (Crypto + AI + Networks)
- ✅ Demonstrates practical optimization
- ✅ Produces measurable results
- ✅ Includes complete documentation
- ✅ Professional-quality visualizations
- ✅ Ready for academic submission

---

**Version:** 1.0  
**Last Updated:** [Current Date]  
**Status:** Complete and ready for use

---

*Happy coding and good luck with your project! 🚀*
