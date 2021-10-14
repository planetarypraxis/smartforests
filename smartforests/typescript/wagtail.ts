import useSWR from "swr"
import qs from 'query-string'

export const wagtailAPIDefaultOptions = {
  'limit': 20,
  'fields': '*'
}

export function useWagtailSearch<Item = any, Wrapper = Wagtail.Results<Item>>(query: Wagtail.APIOptions = {}, url = '/api/v2/pages/') {
  return useSWR<Wrapper>(
    qs.stringifyUrl({
      url,
      query: Object.assign({}, wagtailAPIDefaultOptions, query)
    }),
    url => fetch(url).then(response => response.json()),
    { revalidateOnFocus: false, revalidateOnReconnect: false }
  )
}

export namespace Wagtail {
  export type APIOptions = {
    // search
    type?: string,
    search?: string,
    search_operator?: 'and' | 'or',
    html_path?: string,
    // result
    fields?: string,
    order?: string,
    // list
    offset?: number,
    limit?: number,
    // hierarchy
    id?: number
    child_of?: number,
    ancestor_of?: number,
    descendant_of?: number,
    // i18n
    translation_of?: number,
    locale?: string
  }

  export interface Results<T = {}> {
    meta: ResultsMeta;
    items: Item<T>[];
  }

  export type Item<T = {}> = T & {
    id: number;
    meta: ItemMeta;
    title: string;
  }

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