import React, { FC, useEffect, useMemo, useRef } from "react";

export interface TurboFrameElement extends HTMLElement {
  src?: string;
  target?: string;
}
