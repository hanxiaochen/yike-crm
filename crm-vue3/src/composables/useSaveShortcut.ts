import { onMounted, onUnmounted } from 'vue'

export function useSaveShortcut(callback: () => void) {
  const handleKeydown = (e: KeyboardEvent) => {
    // Mac: Command + Enter (metaKey) | Windows: Ctrl + Enter (ctrlKey)
    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
      e.preventDefault()
      callback()
    }
  }

  onMounted(() => {
    window.addEventListener('keydown', handleKeydown)
  })

  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeydown)
  })
}
