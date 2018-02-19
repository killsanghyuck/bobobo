require 'selenium-webdriver'
require 'faraday'
require 'faraday-cookie_jar'
require 'nokogiri'
require 'json'


KAKAO_HOST_URL = 'https://parking.kakao.com/admin'
AREA_NAME = '알파리움'


HOST_URL = 'http://npgsgranparkingroot.iptime.org'.freeze
LOGIN_URL = '/j_spring_security_check'.freeze
SEARCH_CAR_NUMBER_URL = '/ezTicket/carSearch'.freeze
SEARCH_TICKET_URL = '/ezTicket/carTicket'.freeze
GET_PARK_CODE_URL = '/ezTicket/inputDiscountValue'.freeze
ADD_COUPON_URL = '/ezTicket/valiDiscountCode.json'.freeze
SUBMIT_COUPON_URL = '/ezTicket/inputDiscountValueRegister'.freeze
GRAN_SEOUL_AREA_ID = 58

COUPONS = [{ id: 60, name: '30분쿠폰', value: 30 },
           { id: 61, name: '1시간쿠폰', value: 60 },
           { id: 62, name: '2시간쿠폰', value: 120 },
           { id: 63, name: '3시간쿠폰', value: 180 },
           { id: 64, name: '4시간쿠폰', value: 240 }].freeze


@conn = Faraday.new(url: HOST_URL) do |faraday|
 faraday.request :url_encoded
 faraday.response :logger
 faraday.use :cookie_jar
 faraday.adapter Faraday.default_adapter
end




def initialize(a, b, c)
  # raise 'Reservation is nil' if reservation.nil?
  # raise 'Reservation is not from GranSeoul' unless reservation.area.id.eql?(GRAN_SEOUL_AREA_ID)
  # raise 'Product is nil' if reservation.oper_table_product.nil?

  @real_ti = nil
  @park_code = nil
  @click_count = 0
  @order = { discount_value: '',
             discount_name: [],
             discount_code: [],
             discount_desc: [] }
  @car_number = b.gsub(/[\s+-]/, '')
  @ti = a
  @duration = c
  # init_connection
end

def login?
  response = @conn.post LOGIN_URL, j_username: 'parkhere', j_password: '1234'
  !response.env.response_headers[:location].include?('fail')
end

def find_car_number?
  is_find = false
  response = @conn.post SEARCH_CAR_NUMBER_URL, car_no: @car_number.to_s[-4, 4]
  if response.status.eql?(200)
    Nokogiri::HTML(response.body).css('table > tbody > tr').each do |tr|
      car_number = tr.css('a:first').text unless tr.css('a:first').empty?
      next unless @car_number.eql?(car_number)
      next if tr.css('input:first').empty?
      real_ti = Time.zone.parse(tr.css('input:first').attr('value'))
      next unless real_ti.year.eql?(@ti.year) && real_ti.month.eql?(@ti.month) && real_ti.day.eql?(@ti.day)
      @real_ti = real_ti
      set_duration
      get_park_code
      is_find = true
      break
    end
  end
  is_find
end

def process?
  make_order
  submit_coupon
  is_process = submit_coupon_success?
  logger.debug 'Could not find submit result' unless is_process
  is_process
end

def self.area_id
  GRAN_SEOUL_AREA_ID
end

def get_park_code
  response = @conn.post GET_PARK_CODE_URL, car_no: @car_number, car__totaldate: @real_ti.strftime('%Y%m%d%H%M%S')
  # raise RuntimeError unless response.status.eql?(200)
  park_code_list = Nokogiri::HTML(response.body).xpath('//input[@id="park_code"]')
  @park_code = park_code_list.first.attr('value') unless park_code_list.empty?
end

def make_order
  coupon_times = COUPONS.map { |elem| elem[:value] }
  duration = @duration
  while duration > 0 && !coupon_times.empty?
    if duration >= coupon_times[-1]
      coupon = COUPONS.find { |elem| elem[:value] == coupon_times[-1] }
      add_coupon(coupon)
      duration -= coupon[:value]
    else
      coupon_times.pop
    end
  end

  return unless duration > 0
  coupon = COUPONS.find { |elem| elem[:value] == 30 }
  add_coupon(coupon)
end

def add_coupon(coupon)
  response = @conn.post ADD_COUPON_URL, discount_code: coupon[:id], car_no: @car_number, clickCount: @click_count
  json_body = JSON.parse(response.body)
  @order[:discount_value] = @order[:discount_value].to_i + json_body['dcValue'].to_i
  @order[:discount_name].push(coupon[:name])
  @order[:discount_code].push(coupon[:id])
  @order[:discount_desc].push(json_body['dcDesc'])

  @click_count += 1
end

def submit_coupon
  params = { group_name: '모바일 할인',
             department_name: '파크히어',
             car_no: @car_number,
             park_code: @park_code,
             car_in_date: "#{@real_ti.strftime('%Y-%m-%d')} 00:00:00.0",
             car_in_time: @real_ti.strftime('%H:%M'),
             car__totaldate: @real_ti.strftime('%Y%m%d%H%M%S'),
             discount_name: @order[:discount_name].join(','),
             discount_code: @order[:discount_code].join(','),
             discount_value: @order[:discount_value],
             discount_desc: @order[:discount_desc].join(',') }
  logger.debug params
  @conn.post SUBMIT_COUPON_URL, params
end

def submit_coupon_success?
  response = @conn.post SEARCH_TICKET_URL
  return false unless response.status.eql?(200)

  Nokogiri::HTML(response.body).css('table > tbody > tr').each do |tr|
    td_texts = tr.css('td').map(&:text)
    return true if td_texts.include?(@car_number) && td_texts.include?(@duration.to_s)
  end
  false
end

def set_duration
  to = @real_ti + 60 * @duration
  return if to.day == @real_ti.day
  @duration -= to.hour * 60
  @duration -= (to.min / 30) * 30
end





GranSeoul = GranSeoul.new('2018-02-13 14:10:22', '27구4146', 1080)
if GranSeoul.login?
  puts 'login'
	if GranSeoul.find_car_number?
    puts 'find car number!'
	GranSeoul.process?
  else
    puts 'cant find car number :('
  end
end

Selenium::WebDriver::Chrome.driver_path = ('/Users/gilsanghyeog/Documents/chromedriver')
driver = Selenium::WebDriver.for :chrome
driver.get(HOST_URL + '/login')
driver.find_element(name: 'manager[login]').send_keys('san.kill')
driver.find_element(name: 'manager[password]').send_keys('!@dl926516')
driver.find_element(name: 'commit').click()
driver.get(HOST_URL + '/picks?q[parking_lot_name_cont]=' + AREA_NAME + '&q[state_eq]=4&order=id_desc')
driver.page_source
