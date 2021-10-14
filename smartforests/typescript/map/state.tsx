import { atom, useAtom, WritableAtom } from "jotai"
import { atomFamily } from "jotai/utils"

type FocusID = number
export const focusIdAtom = atom<FocusID | 0>(0)
export const setFocusIdAtom = atom(null, (get, set, value: FocusID | null) => set(focusIdAtom, value))

type FocusType = string // 'logbooks.LogbookPage' | 'logbooks.LogbookEntryPage' | 'logbooks.StoryPage'
export const focusTypeAtom = atom<FocusType | ''>('')
export const setFocusTypeAtom = atom(null, (get, set, value: FocusType | null) => set(focusTypeAtom, value))

type FocusSource = 'list' | 'map' | 'url'
export const focusSourceAtom = atom<FocusSource | ''>('url')
export const setFocusSourceAtom = atom(null, (get, set, value: FocusSource | null) => set(focusSourceAtom, value))

export const isFocused = atomFamily((FocusId: FocusID) => atom(
  get => get(focusIdAtom) === FocusId,
  (get, set, FocusId: FocusID | null) => set(focusIdAtom as any, FocusId)
))

export const useFocusContext = (FocusId: FocusID, type: FocusType) => {
  const [FocusSource, setFocusSource] = useAtom(focusSourceAtom)
  const [, setFocusType] = useAtom(focusTypeAtom)
  const [thisIsFocused, setFocusId] = useAtom(isFocused(FocusId))
  return [
    thisIsFocused,
    (isFocusing: boolean, nextFocusSource: FocusSource) => {
      setFocusSource(nextFocusSource)
      setFocusType(type)
      setFocusId(isFocusing ? FocusId : null)
    },
    FocusSource
  ] as const
}
