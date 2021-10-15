export namespace SmartForest {
  export interface LogbookPage {
    tags: string[];
    description: string;
    geographical_location?: string;
    contributors: Contributor[];
    coordinates?: Coordinates;
  }

  export interface Contributor {
  }

  export interface Coordinates {
    type: string;
    coordinates: number[];
  }
}