export namespace SmartForest {
  export interface StoryPage extends GeocodedMixin {
    tags: string[];
  }

  export interface LogbookPage extends GeocodedMixin {
    tags: string[];
    description: string;
  }

  export interface LogbookEntryPage extends GeocodedMixin {
    tags: string[];
  }

  export interface GeocodedMixin {
    geographical_location?: string;
    coordinates?: Coordinates;
    label: string;
  }

  export interface Contributor {
  }

  export interface Coordinates {
    type: string;
    coordinates: number[];
  }
}