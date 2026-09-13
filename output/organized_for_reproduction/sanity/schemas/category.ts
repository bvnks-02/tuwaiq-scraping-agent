import {defineType, defineField} from 'sanity'

export const category = defineType({
  name: 'category',
  title: 'Category (التصنيف)',
  type: 'document',
  fields: [
    defineField({name: 'titleAr', title: 'Title (AR)', type: 'string', validation: r => r.required()}),
    defineField({name: 'titleEn', title: 'Title (EN)', type: 'string'}),
    defineField({name: 'slug', title: 'Slug', type: 'slug', options: {source: 'titleAr'}, validation: r => r.required()}),
    defineField({name: 'description', title: 'Description', type: 'text'}),
    defineField({name: 'color', title: 'Brand Color', type: 'string', description: 'Hex, e.g. #4f29b7'}),
    defineField({name: 'image', title: 'Icon', type: 'image', options: {hotspot: true}}),
  ],
  preview: {select: {title: 'titleAr', subtitle: 'titleEn'}}
})
