import React from "react";
import useSWR from "swr";
import qs from "query-string";
import { SmartForest } from "./map/types";
import { getLanguageCode } from './pageContext';

export const wagtailAPIDefaultOptions = {
  limit: 20,
  fields: "*",
};

export const initialPageURL = () =>
  new URL(
    JSON.parse(document.getElementById("routing_configuration").textContent)
  );

export function pageToPath(page: Wagtail.Item): string {
  return `${initialPageURL().pathname}${page.meta.type.split(".").join("/")}/${
    page.id
  }`;
}

export function constructModelTypeName(
  model: string,
  modelName: string
): string {
  return [model, modelName].join(".");
}

export function pageToFrameURL(page: SmartForest.MapItem["page"]) {
  const languageCode = getLanguageCode()
  return `${languageCode ? `/${languageCode}` : ""}/_frame/${page.id}`;
}

export function useWagtailSearch<Item = any, Wrapper = Wagtail.Results<Item>>(
  query: Wagtail.APIOptions = {},
  url = "/api/v2/pages/"
) {
  return useSWR<Wrapper>(
    qs.stringifyUrl({
      url,
      query: Object.assign({}, wagtailAPIDefaultOptions, query),
    }),
    (url) => fetch(url).then((response) => response.json()),
    { revalidateOnFocus: false, revalidateOnReconnect: false }
  );
}

export namespace Wagtail {
  export type APIOptions = {
    // search
    type?: string | string[];
    search?: string;
    search_operator?: "and" | "or";
    html_path?: string;
    // result
    fields?: string;
    order?: string;
    // list
    offset?: number;
    limit?: number;
    // hierarchy
    id?: number;
    child_of?: number;
    ancestor_of?: number;
    descendant_of?: number;
    // i18n
    translation_of?: number;
    locale?: string;
  };

  export interface Results<T = {}> {
    meta: ResultsMeta;
    items: Item<T>[];
  }

  export type Item<T = {}> = T & {
    id: number;
    meta: ItemMeta;
    title: string;
    icon_class?: string;
  };

  interface ItemMeta {
    type: string;
    detail_url: string;
    html_url: string;
    slug: string;
    show_in_menus: boolean;
    seo_title: string;
    search_description: string;
    first_published_at: Date;
    locale: string;
  }

  interface ResultsMeta {
    total_count: number;
  }
}
