import { render, type RenderOptions } from '@testing-library/react'
import { ThemeContext } from '@/lib/theme-context'
import type { ReactElement } from 'react'

interface CustomRenderOptions extends RenderOptions {
  theme?: 'light' | 'dark'
  toggleTheme?: () => void
}

function renderWithProviders(
  ui: ReactElement,
  options?: CustomRenderOptions,
) {
  const { theme = 'light', toggleTheme = () => {}, ...rest } = options || {}
  const value = { theme, toggleTheme }
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>
  )
  return render(ui, { wrapper, ...rest })
}

export * from '@testing-library/react'
export { renderWithProviders as render }
