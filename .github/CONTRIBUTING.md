## 🤝 Contributing  

We welcome contributions to **Chat with Logs**! Whether you’re fixing bugs, improving documentation, or adding new features, your help is appreciated.  

### 📝 How to Contribute  

1. **Fork the Repository**  
   Click the **Fork** button at the top right of this repo and clone it locally:  

   ```bash
   git clone git@github.com:dingus-technology/CHAT-WITH-LOGS.git
   ```

2. **Create a New Branch**  
   Use a descriptive name for your branch:  

   ```bash
   git checkout -b feature/new-awesome-feature
   ```

    ### 🔹 **Branch Naming Conventions**  

    | **Prefix**            | **Purpose**                                                            | **Example**                      |
    | --------------------- | ---------------------------------------------------------------------- | -------------------------------- |
    | **`feature/`**        | For new features or enhancements                                       | `feature/add-logging-support`    |
    | **`fix/`**            | For bug fixes                                                          | `fix/loki-url-connection`        |
    | **`chore/`**          | For maintenance tasks (e.g., refactoring, dependency updates)          | `chore/update-dependencies`      |
    | **`hotfix/`**         | For urgent fixes in production                                         | `hotfix/fix-auth-token-bug`      |
    | **`refactor/`**       | For restructuring or improving existing code without changing behavior | `refactor/clean-api-handlers`    |
    | **`docs/`**           | For documentation updates                                              | `docs/update-readme`             |
    | **`test/`**           | For adding or updating tests                                           | `test/integration-tests-logging` |
    | **`release/`**        | For preparing a new release                                            | `release/v1.2.0`                 |
    | **`ci/` or `build/`** | For CI/CD pipeline updates                                             | `ci/update-github-actions`       |

    💡 **Best Practices**:  
    - Use **kebab-case** (hyphen-separated words) for readability.  
    - Keep branch names **descriptive** but **concise**.  
    - Use issue/ticket numbers when relevant (e.g., `feature/123-add-user-auth`).  
  
3. **Make Your Changes**  
   - Ensure your code is clean and well-documented.  
   - Run code checks before committing:  

     ```bash
     format-checks
     code-checks
     ```

4. **Commit and Push**  
   ```bash
   git add .
   git commit -m "Add feature: new awesome functionality"
   git push origin feature/new-awesome-feature
   ```

5. **Submit a Pull Request (PR)**  
   - Open a PR against the `main` branch.  
   - Provide a clear description of the changes and their purpose.  
   - Follow the `PULL_REQUEST_TEMPLATE.md`.

### 🐛 Reporting Issues  

Found a bug? Have a feature request? Please **open an issue** [here](https://github.com/dingus-technology/chat-with-logs/issues) with:  
- A clear description of the issue.
- Steps to reproduce (if applicable). 
- Expected vs. actual behavior.
- Screenshot of issue.

### ✅ Contribution Guidelines  

- Ensure your changes align with the project's goal.  
- Follow the existing coding style and structure.  
- Write meaningful commit messages - emojis encouraged i.e. `🐛 fix: bug removed`.
- Leave no trace - do not leave comments - clear code and doc strings alleviate the need for comments.

---

💡 **Join us in making debugging smarter and faster!** 🚀