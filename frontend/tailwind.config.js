/** @type {import('tailwindcss').Config} */
export default {
    content: ['./src/**/*.{html,js,svelte,ts}'],
    theme: {
      extend: {
          colors:{
              "jax-blue":"#4e96fd",
              "jax-green":"#00a99a",
              "jax-purple":"#ab00b6",
              "jax-yellow":"#ffd900",
              "jax-blue-hover":"#61a0fa"
          }
      },
    },
    plugins: [],
  }  