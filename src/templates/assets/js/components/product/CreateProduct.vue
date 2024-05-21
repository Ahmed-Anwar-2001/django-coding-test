<template>
  <section>
    <div class="row">
      <div class="col-md-6">
        <div class="card shadow mb-4">
          <div class="card-body">
            <div class="form-group">
              <label for="">Product Name</label>
              <input type="text" v-model="product_name" placeholder="Product Name" class="form-control">
            </div>
            <div class="form-group">
              <label for="">Product SKU</label>
              <input type="text" v-model="product_sku" placeholder="Product SKU" class="form-control">
            </div>
            <div class="form-group">
              <label for="">Description</label>
              <textarea v-model="description" cols="30" rows="4" class="form-control"></textarea>
            </div>
          </div>
        </div>

        <div class="card shadow mb-4">
          <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
            <h6 class="m-0 font-weight-bold text-primary">Media</h6>
          </div>
          <div class="card-body border">
            <vue-dropzone ref="myVueDropzone" id="dropzone" :options="dropzoneOptions"></vue-dropzone>
          </div>
        </div>
      </div>

      <div class="col-md-6">
        <div class="card shadow mb-4">
          <div class="card-header py-3 d-flex flex-row align-items-center justify-content-between">
            <h6 class="m-0 font-weight-bold text-primary">Variants</h6>
          </div>
          <div class="card-body">
            <div class="row" v-for="(item, index) in product_variant" :key="index">
              <div class="col-md-4">
                <div class="form-group">
                  <label for="">Option</label>
                  <select v-model="item.option" class="form-control">
                    <option v-for="variant in variants" :key="variant.id" :value="variant.id">
                      {{ variant.title }}
                    </option>
                  </select>
                </div>
              </div>
              <div class="col-md-8">
                <div class="form-group">
                  <label v-if="product_variant.length != 1" @click="removeVariant(index)" class="float-right text-primary" style="cursor: pointer;">
                    Remove
                  </label>
                  <label v-else>.</label>
                  <input-tag v-model="item.tags" @input="checkVariant" class="form-control"></input-tag>
                </div>
              </div>
            </div>
          </div>
          <div class="card-footer" v-if="canAddVariant">
            <button @click="newVariant" class="btn btn-primary">Add another option</button>
          </div>

          <div class="card-header text-uppercase">Preview</div>
          <div class="card-body">
            <div class="table-responsive">
              <table class="table">
                <thead>
                  <tr>
                    <td>Variant</td>
                    <td>Price</td>
                    <td>Stock</td>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(variant_price, index) in product_variant_prices" :key="index">
                    <td>{{ variant_price.title }}</td>
                    <td>
                      <input type="text" class="form-control" v-model="variant_price.price">
                    </td>
                    <td>
                      <input type="text" class="form-control" v-model="variant_price.stock">
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>

    <button @click="saveProduct" type="submit" class="btn btn-lg btn-primary">Save</button>
    <button type="button" class="btn btn-secondary btn-lg" @click="cancel">Cancel</button>
  </section>
</template>

<script>
import vue2Dropzone from 'vue2-dropzone'
import 'vue2-dropzone/dist/vue2Dropzone.min.css'
import InputTag from 'vue-input-tag'
import axios from 'axios'

export default {
  components: {
    vueDropzone: vue2Dropzone,
    InputTag
  },
  props: {
    variants: {
      type: Array,
      required: true
    },
    product: {
      type: Object,
      default: () => ({
        title: '',
        sku: '',
        description: '',
        id: null
      })
    },
    productVariants: {
      type: Array,
      default: () => []
    },
    productVariantPrices: {
      type: Array,
      default: () => []
    }
  },
  data() {
    return {
      product_name: this.product.title,
      product_sku: this.product.sku,
      description: this.product.description,
      images: [],
      product_variant: this.productVariants.length ? this.productVariants.map(v => ({
        option: v['variant__id'],
        tags: v.variant_title.split('/')
      })) : [{
        option: this.variants[0]?.id,
        tags: []
      }],
      product_variant_prices: this.productVariantPrices.length ? this.productVariantPrices.map(p => ({
        title: [p.product_variant_one, p.product_variant_two, p.product_variant_three].filter(Boolean).join('/'),
        price: p.price,
        stock: p.stock
      })) : [],
      dropzoneOptions: {
        url: 'https://httpbin.org/post',
        thumbnailWidth: 150,
        maxFilesize: 0.5,
        headers: {"My-Awesome-Header": "header value"}
      }
    }
  },
  computed: {
    canAddVariant() {
      return this.product_variant.length < this.variants.length && this.product_variant.length < 3;
    }
  },
  methods: {
    newVariant() {
      const all_variants = this.variants.map(el => el.id);
      const selected_variants = this.product_variant.map(el => el.option);
      const available_variants = all_variants.filter(variant => !selected_variants.includes(variant));
      
      if (available_variants.length > 0) {
        this.product_variant.push({
          option: available_variants[0],
          tags: []
        });
      }
    },
    removeVariant(index) {
      this.product_variant.splice(index, 1);
      this.checkVariant();
    },
    checkVariant() {
      const tags = this.product_variant.map(item => item.tags);
      this.product_variant_prices = this.getCombn(tags).map(combination => ({
        title: combination,
        price: 0,
        stock: 0
      }));
    },
    getCombn(arr, pre = '') {
      if (!arr.length) {
        return pre;
      }
      return arr[0].reduce((acc, value) => acc.concat(this.getCombn(arr.slice(1), pre + value + '/')), []);
    },
    async saveProduct() {
      const product = {
        title: this.product_name,
        sku: this.product_sku,
        description: this.description,
        product_image: this.images,
        product_variant: this.product_variant,
        product_variant_prices: this.product_variant_prices
      };

      try {
        const csrfResponse = await axios.get('/product/get-csrf-token/');
        const csrfToken = csrfResponse.data.csrfToken;
        
        axios.defaults.headers.common['X-CSRFToken'] = csrfToken;

        if (this.product.id) {
          const response = await axios.post(`/product/api/update/${this.product.id}/`, product);
          console.log(response.data);
        } else {
          const response = await axios.post('/product/api/create/', product);
          console.log(response.data);
        }
        
        // Redirect to product list page after successful creation or update
        window.location.href = '/product/list/';
      } catch (error) {
        console.error('Error saving product:', error);
      }
    },
    addImage(file, dataUrl) {
      this.images.push(dataUrl);
    },
    cancel() {
      window.location.href = '/product/list/';
    }
  },
  mounted() {
    console.log('Component mounted.');
  }
}
</script>
