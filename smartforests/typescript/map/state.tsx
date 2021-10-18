import { atom, useAtom, WritableAtom } from "jotai";
import { atomFamily, useUpdateAtom } from "jotai/utils";

type FocusID = string | number;
export const focusIdAtom = atom<FocusID>("0");

type FocusType = string; // 'logbooks.LogbookPage' | 'logbooks.LogbookEntryPage' | 'logbooks.LogbookEntryPage'
export const focusTypeAtom = atom<FocusType | "">("");

type FocusSource = "list" | "map" | "url";
export const focusSourceAtom = atom<FocusSource | "">("url");

export const isFocused = atomFamily((FocusId: FocusID) =>
  atom(
    (get) => get(focusIdAtom) === FocusId,
    (get, set, FocusId: FocusID | null) => set(focusIdAtom as any, FocusId)
  )
);

export const useFocusContext = (focusId: FocusID, type: FocusType) => {
  const [focusSource, setFocusSource] = useAtom(focusSourceAtom);
  const setFocusType = useUpdateAtom(focusTypeAtom);
  const [thisIsFocused, setFocusId] = useAtom(isFocused(focusId));
  return [
    thisIsFocused,
    (
      isFocusing: boolean,
      nextFocusSource: FocusSource,
      nextFocusId: FocusID = focusId
    ) => {
      setFocusSource(nextFocusSource);
      setFocusType(type);
      setFocusId(isFocusing ? focusId : null);
    },
    focusSource,
  ] as const;
};
