import {defineType, defineField} from 'sanity'
export const libraryArticle = defineType({
  name: 'libraryArticle',
  title: 'Library Item (مكتبة طويق)',
  type: 'document',
  fields: [
    defineField({name: 'titleAr', title: 'Title (AR)', type: 'string', validation: r => r.required()}),
    defineField({name: 'slug', title: 'Slug', type: 'slug', options: {source: 'titleAr'}}),
    defineField({name: 'descriptionAr', title: 'Description (AR)', type: 'text'}),
    defineField({name: 'excerpt', title: 'Excerpt', type: 'text'}),
    defineField({name: 'contentHtml', title: 'Content (HTML, RTL)', type: 'array', of: [{type: 'block'}], description: 'Convert contentHtml to Portable Text on import; special-case externalPdf items'}),
    defineField({name: 'externalPdf', title: 'External PDF URL (magazines/publications)', type: 'url'}),
    defineField({name: 'sourceType', title: 'Type', type: 'string', options: {list: ['ARTICLE','PUBLICATION','MAGAZINE']}}),
    defineField({name: 'keywords', title: 'Keywords', type: 'array', of: [{type: 'string'}]}),
    defineField({name: 'duration', title: 'Read Duration (min)', type: 'number'}),
    defineField({name: 'logoUrl', title: 'Cover URL', type: 'url'}),
    defineField({name: 'visitorCount', title: 'Visitors', type: 'number'}),
    defineField({name: 'publishedAt', title: 'Published At', type: 'datetime'}),
    defineField({name: 'url', title: 'Source URL', type: 'url'}),
  ],
  preview: {select: {title: 'titleAr', subtitle: 'sourceType'}}
})
