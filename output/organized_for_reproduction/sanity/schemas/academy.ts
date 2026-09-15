import {defineType, defineField} from 'sanity'
export const academy = defineType({
  name: 'academy',
  title: 'Academy (طويق / subs)',
  type: 'document',
  fields: [
    defineField({name: 'titleAr', title: 'Name (AR)', type: 'string'}),
    defineField({name: 'titleEn', title: 'Name (EN)', type: 'string'}),
    defineField({name: 'code', title: 'Code', type: 'string'}),
    defineField({name: 'logo', title: 'Logo URL', type: 'url'}),
  ]
})
