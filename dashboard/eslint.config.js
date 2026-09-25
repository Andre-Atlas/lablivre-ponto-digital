import js from '@eslint/js';
import tseslint from 'typescript-eslint';

// Configuração do ESLint 9 (Flat Config) para React e TypeScript
export default tseslint.config(
  { ignores: ['dist', 'node_modules'] },
  {
    extends: [js.configs.recommended, ...tseslint.configs.recommended],
    files: ['**/*.{ts,tsx}'],
    languageOptions: {
      ecmaVersion: 2022,
    },
    rules: {
      // Regras e personalizações adicionais do squad
    },
  },
);
